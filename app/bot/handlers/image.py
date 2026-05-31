from __future__ import annotations

from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.agents.orchestrator import AgentContext, OrchestratorAgent
from app.bot.keyboards.common import cancel_keyboard, main_menu_keyboard
from app.config.settings import get_settings
from app.ocr.pipeline import OCRPipeline
from app.services.memory import add_to_history
from app.utils.helpers import clean_latex_for_telegram
from app.utils.i18n import _, resolve_lang

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
    lang = resolve_lang(event.from_user.language_code if event.from_user else None)
    text = _("image_prompt", lang)
    await state.set_state(ImageStates.waiting_for_image)
    if isinstance(event, Message):
        await event.answer(text, reply_markup=cancel_keyboard(lang))
    else:
        await event.message.edit_text(text, reply_markup=cancel_keyboard(lang))
        await event.answer()


@router.message(ImageStates.waiting_for_image, F.photo)
async def handle_photo(message: Message, state: FSMContext) -> None:
    lang = resolve_lang(message.from_user.language_code if message.from_user else None)
    if not message.photo:
        return

    photo = message.photo[-1]
    processing_msg = await message.answer(_("processing_image", lang))

    try:
        file = await message.bot.get_file(photo.file_id)
        file_bytes = await message.bot.download_file(file.file_path)

        ocr_result = await ocr_pipeline.process(
            file_bytes.read(),
            filename=f"{photo.file_id}.jpg",
        )

        if not ocr_result.text.strip():
            await processing_msg.edit_text(
                _("no_text_found", lang),
                reply_markup=main_menu_keyboard(lang),
            )
            await state.clear()
            return

        review = _("low_confidence", lang) if ocr_result.needs_review else ""
        await processing_msg.edit_text(
            _("extracted_text", lang,
              text=ocr_result.text[:500] + ("..." if len(ocr_result.text) > 500 else ""),
              confidence=ocr_result.confidence,
              review=review),
        )

        user = message.from_user
        context = AgentContext(
            user_id=str(user.id) if user else "unknown",
            language=user.language_code if user else "en",
            metadata={"ocr_text": ocr_result.text, "ocr_confidence": ocr_result.confidence},
        )

        result = await orchestrator.solve("", context, ocr_text=ocr_result.text)

        response = clean_latex_for_telegram(result.final_answer)

        if user:
            await add_to_history(user.id, "user", ocr_result.text)
            await add_to_history(user.id, "assistant", result.final_answer)

        if len(response) > 4000:
            for i in range(0, len(response), 4000):
                chunk = response[i : i + 4000]
                try:
                    await message.answer(chunk, parse_mode="Markdown")
                except Exception:
                    await message.answer(chunk, parse_mode=None)
        else:
            try:
                await processing_msg.edit_text(response, parse_mode="Markdown")
            except Exception:
                await processing_msg.edit_text(response, parse_mode=None)

    except Exception as e:
        await processing_msg.edit_text(
            _("error_ocr", lang, error=str(e)[:200]),
            reply_markup=main_menu_keyboard(lang),
            parse_mode=None,
        )
    finally:
        await state.clear()


@router.message(ImageStates.waiting_for_image, F.document)
async def handle_document(message: Message, state: FSMContext) -> None:
    lang = resolve_lang(message.from_user.language_code if message.from_user else None)
    if not message.document:
        return

    doc = message.document
    ext = Path(doc.file_name or "file.png").suffix.lower().lstrip(".")
    if ext not in settings.SUPPORTED_IMAGE_FORMATS:
        await message.answer(
            _("unsupported_format", lang, ext=ext, formats=", ".join(settings.SUPPORTED_IMAGE_FORMATS))
        )
        return

    if doc.file_size and doc.file_size > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
        await message.answer(_("file_too_large", lang, max_size=settings.MAX_IMAGE_SIZE_MB))
        return

    processing_msg = await message.answer(_("processing_image", lang))

    try:
        file = await message.bot.get_file(doc.file_id)
        file_bytes = await message.bot.download_file(file.file_path)

        ocr_result = await ocr_pipeline.process(
            file_bytes.read(),
            filename=doc.file_name or "document.png",
        )

        if not ocr_result.text.strip():
            await processing_msg.edit_text(
                _("no_text_found", lang),
                reply_markup=main_menu_keyboard(lang),
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

        response = clean_latex_for_telegram(result.final_answer)

        if user:
            await add_to_history(user.id, "user", ocr_result.text)
            await add_to_history(user.id, "assistant", result.final_answer)

        if len(response) > 4000:
            for i in range(0, len(response), 4000):
                chunk = response[i : i + 4000]
                try:
                    await message.answer(chunk, parse_mode="Markdown")
                except Exception:
                    await message.answer(chunk, parse_mode=None)
        else:
            try:
                await processing_msg.edit_text(response, parse_mode="Markdown")
            except Exception:
                await processing_msg.edit_text(response, parse_mode=None)

    except Exception as e:
        await processing_msg.edit_text(
            _("error_ocr", lang, error=str(e)[:200]),
            reply_markup=main_menu_keyboard(lang),
            parse_mode=None,
        )
    finally:
        await state.clear()
