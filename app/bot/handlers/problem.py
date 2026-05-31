from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.agents.orchestrator import AgentContext, OrchestratorAgent
from app.bot.keyboards.common import cancel_keyboard, main_menu_keyboard, subject_keyboard
from app.config.settings import get_settings
from app.utils.helpers import clean_latex_for_telegram
from app.utils.i18n import _, resolve_lang

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
    lang = resolve_lang(event.from_user.language_code if event.from_user else None)
    text = _("solve_prompt", lang)
    await state.set_state(ProblemStates.waiting_for_problem)
    if isinstance(event, Message):
        await event.answer(text, reply_markup=cancel_keyboard(lang))
    else:
        await event.message.edit_text(text, reply_markup=cancel_keyboard(lang))
        await event.answer()


@router.message(ProblemStates.waiting_for_problem)
async def handle_problem_text(message: Message, state: FSMContext) -> None:
    lang = resolve_lang(message.from_user.language_code if message.from_user else None)
    if not message.text:
        await message.answer(_("send_text_or_image", lang), reply_markup=cancel_keyboard(lang))
        return
    prompt = message.text.strip()
    if len(prompt) > settings.MAX_PROMPT_LENGTH:
        await message.answer(_("too_long", lang, max=settings.MAX_PROMPT_LENGTH))
        return

    user = message.from_user
    if not user:
        return

    await state.update_data(prompt=prompt)
    await state.set_state(ProblemStates.waiting_for_subject)

    await message.answer(
        _("select_subject", lang),
        reply_markup=subject_keyboard(lang),
    )


@router.callback_query(ProblemStates.waiting_for_subject, F.data.startswith("subject:"))
async def handle_subject_selection(callback: CallbackQuery, state: FSMContext) -> None:
    lang = resolve_lang(callback.from_user.language_code if callback.from_user else None)
    subject = callback.data.split(":", 1)[1]
    data = await state.get_data()
    prompt = data.get("prompt", "")
    user = callback.from_user

    if not user or not prompt:
        await callback.message.edit_text(
            _("something_wrong", lang), reply_markup=main_menu_keyboard(lang)
        )
        await state.clear()
        return

    await state.set_state(ProblemStates.processing)
    processing_msg = await callback.message.edit_text(
        _("analyzing", lang),
        reply_markup=None,
    )

    context = AgentContext(
        user_id=str(user.id),
        language=user.language_code or "en",
        subject=subject,
    )

    try:
        result = await orchestrator.solve(prompt, context)

        if result.error:
            await processing_msg.edit_text(
                _("ai_error", lang, error=result.error),
                reply_markup=main_menu_keyboard(lang),
            )
            await state.clear()
            return

        response_parts = []
        response_parts.append(result.final_answer)

        if result.plan.needs_validation and result.validation_result and result.validation_result.confidence < 0.7:
            response_parts.append(
                _("validation_note", lang, confidence=result.validation_result.confidence)
            )

        response = "\n".join(response_parts)
        response = clean_latex_for_telegram(response)

        if len(response) > 4000:
            for i in range(0, len(response), 4000):
                chunk = response[i : i + 4000]
                try:
                    await callback.message.answer(chunk, parse_mode="Markdown")
                except Exception:
                    await callback.message.answer(chunk, parse_mode=None)
        else:
            try:
                await processing_msg.edit_text(response, parse_mode="Markdown")
            except Exception:
                await processing_msg.edit_text(response, parse_mode=None)

    except Exception as e:
        await processing_msg.edit_text(
            _("processing_error", lang, error=str(e)[:200]),
            reply_markup=main_menu_keyboard(lang),
            parse_mode=None,
        )

    finally:
        await state.clear()


@router.message(ProblemStates.processing)
async def ignore_during_processing(message: Message) -> None:
    lang = resolve_lang(message.from_user.language_code if message.from_user else None)
    await message.answer(_("wait_processing", lang))
