from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.agents.orchestrator import AgentContext, OrchestratorAgent
from app.bot.keyboards.common import subject_keyboard, cancel_keyboard, main_menu_keyboard
from app.config.settings import get_settings
from app.services.memory import get_user_context

settings = get_settings()
router = Router(name="problem")
orchestrator = OrchestratorAgent()


class ProblemStates(StatesGroup):
    waiting_for_problem = State()
    waiting_for_subject = State()
    processing = State()


@router.message(Command("solve"))
@router.callback_query(F.data == "solve")
async def cmd_solve(event: Message | CallbackQuery, state: FSMContext) -> None:
    text = "Please send me the problem you want me to solve. You can type it or upload an image."
    await state.set_state(ProblemStates.waiting_for_problem)
    if isinstance(event, Message):
        await event.answer(text, reply_markup=cancel_keyboard())
    else:
        await event.message.edit_text(text, reply_markup=cancel_keyboard())
        await event.answer()


@router.message(ProblemStates.waiting_for_problem)
async def handle_problem_text(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("Please send text or an image.", reply_markup=cancel_keyboard())
        return
    prompt = message.text.strip()
    if len(prompt) > settings.MAX_PROMPT_LENGTH:
        await message.answer(f"Problem too long. Max {settings.MAX_PROMPT_LENGTH} characters.")
        return

    user = message.from_user
    if not user:
        return

    context = await get_user_context(user)
    await state.update_data(prompt=prompt)
    await state.set_state(ProblemStates.waiting_for_subject)

    await message.answer(
        "Select the subject area for better results:",
        reply_markup=subject_keyboard(),
    )


@router.callback_query(ProblemStates.waiting_for_subject, F.data.startswith("subject:"))
async def handle_subject_selection(callback: CallbackQuery, state: FSMContext) -> None:
    subject = callback.data.split(":", 1)[1]
    data = await state.get_data()
    prompt = data.get("prompt", "")
    user = callback.from_user

    if not user or not prompt:
        await callback.message.edit_text("Something went wrong. Please start again.", reply_markup=main_menu_keyboard())
        await state.clear()
        return

    await state.set_state(ProblemStates.processing)
    processing_msg = await callback.message.edit_text(
        "🧠 Analyzing your problem...\nThis may take a moment.",
        reply_markup=None,
    )

    context = AgentContext(
        user_id=str(user.id),
        language=user.language_code or "en",
        subject=subject,
    )

    try:
        result = await orchestrator.solve(prompt, context)

        response_parts = []
        response_parts.append(result.final_answer)

        if result.plan.needs_validation and result.validation_result:
            if result.validation_result.confidence < 0.7:
                response_parts.append(
                    f"\n\n⚠️ *Validation confidence: {result.validation_result.confidence:.0%}*"
                )

        response = "\n".join(response_parts)

        if len(response) > 4000:
            for i in range(0, len(response), 4000):
                chunk = response[i : i + 4000]
                await callback.message.answer(chunk, parse_mode="Markdown")
        else:
            await processing_msg.edit_text(response, parse_mode="Markdown")

    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Sorry, I encountered an error while solving your problem.\n\n"
            f"Error: {str(e)[:200]}\n\nPlease try again or rephrase your question.",
            reply_markup=main_menu_keyboard(),
        )

    finally:
        await state.clear()


@router.message(ProblemStates.processing)
async def ignore_during_processing(message: Message) -> None:
    await message.answer("Please wait, I'm still processing your previous request...")
