from __future__ import annotations

import io
from pathlib import Path

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.agents.orchestrator import AgentContext, OrchestratorAgent
from app.bot.keyboards.common import cancel_keyboard, main_menu_keyboard
from app.config.settings import get_settings
from app.ocr.pipeline import OCRPipeline
from app.services.memory import get_user_context

settings = get_settings()
router = Router(name="image")
ocr_pipeline = OCRPipeline()
orchestrator = OrchestratorAgent()


class ImageStates(StatesGroup):
    waiting_for_image = State()
    processing = State()


@router.message(Command("image"))
@router.callback_query(F.data == "image")
async def cmd_image(event: Message | CallbackQuery, state: FSMContext) -> None:
    text = "Please send me an image of the problem. Supported formats: PNG, JPG, JPEG, BMP, TIFF, WebP"
    await state.set_state(ImageStates.waiting_for_image)
    if isinstance(event, Message):
        await event.answer(text, reply_markup=cancel_keyboard())
    else:
        await event.message.edit_text(text, reply_markup=cancel_keyboard())
        await event.answer()


@router.message(ImageStates.waiting_for_image, F.photo)
async def handle_photo(message: Message, state: FSMContext) -> None:
    if not message.photo:
        return

    photo = message.photo[-1]
    processing_msg = await message.answer("📸 Processing image with OCR...")

    try:
        file = await message.bot.get_file(photo.file_id)
        file_bytes = await message.bot.download_file(file.file_path)

        ocr_result = await ocr_pipeline.process(
            file_bytes.read(),
            filename=f"{photo.file_id}.jpg",
        )

        if not ocr_result.text.strip():
            await processing_msg.edit_text(
                "❌ Could not extract text from the image. Please try with a clearer image.",
                reply_markup=main_menu_keyboard(),
            )
            await state.clear()
            return

        await processing_msg.edit_text(
            f"📝 **Extracted Text:**\n{ocr_result.text[:500]}{'...' if len(ocr_result.text) > 500 else ''}\n\n"
            f"Confidence: {ocr_result.confidence:.0%}\n"
            f"{'⚠️ Low confidence - results may need review.' if ocr_result.needs_review else ''}\n\n"
            f"🧠 Now solving...",
        )

        user = message.from_user
        context = AgentContext(
            user_id=str(user.id) if user else "unknown",
            language=user.language_code if user else "en",
            metadata={"ocr_text": ocr_result.text, "ocr_confidence": ocr_result.confidence},
        )

        result = await orchestrator.solve("", context, ocr_text=ocr_result.text)

        response = result.final_answer
        if len(response) > 4000:
            for i in range(0, len(response), 4000):
                await message.answer(response[i : i + 4000], parse_mode="Markdown")
        else:
            await processing_msg.edit_text(response, parse_mode="Markdown")

    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Error processing image: {str(e)[:200]}",
            reply_markup=main_menu_keyboard(),
        )
    finally:
        await state.clear()


@router.message(ImageStates.waiting_for_image, F.document)
async def handle_document(message: Message, state: FSMContext) -> None:
    if not message.document:
        return

    doc = message.document
    ext = Path(doc.file_name or "file.png").suffix.lower().lstrip(".")
    if ext not in settings.SUPPORTED_IMAGE_FORMATS:
        await message.answer(
            f"Unsupported format: {ext}. Supported: {', '.join(settings.SUPPORTED_IMAGE_FORMATS)}"
        )
        return

    if doc.file_size and doc.file_size > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
        await message.answer(f"File too large. Max size: {settings.MAX_IMAGE_SIZE_MB}MB")
        return

    processing_msg = await message.answer("📸 Processing document...")

    try:
        file = await message.bot.get_file(doc.file_id)
        file_bytes = await message.bot.download_file(file.file_path)

        ocr_result = await ocr_pipeline.process(
            file_bytes.read(),
            filename=doc.file_name or "document.png",
        )

        if not ocr_result.text.strip():
            await processing_msg.edit_text(
                "❌ Could not extract text from the document.",
                reply_markup=main_menu_keyboard(),
            )
            await state.clear()
            return

        user = message.from_user
        context = AgentContext(
            user_id=str(user.id) if user else "unknown",
            language=user.language_code if user else "en",
            metadata={"ocr_text": ocr_result.text, "ocr_confidence": ocr_result.confidence},
        )

        result = await orchestrator.solve("", context, ocr_text=ocr_result.text)

        response = result.final_answer
        if len(response) > 4000:
            for i in range(0, len(response), 4000):
                await message.answer(response[i : i + 4000], parse_mode="Markdown")
        else:
            await processing_msg.edit_text(response, parse_mode="Markdown")

    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Error: {str(e)[:200]}",
            reply_markup=main_menu_keyboard(),
        )
    finally:
        await state.clear()
