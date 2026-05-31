from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.bot.keyboards.common import main_menu_keyboard
from app.services.memory import get_conversation_history
from app.utils.i18n import _, resolve_lang

router = Router(name="history")


@router.callback_query(F.data == "history")
async def show_history(callback: CallbackQuery) -> None:
    user = callback.from_user
    if not user:
        return
    lang = resolve_lang(user.language_code)
    history = await get_conversation_history(user.id, limit=10)
    if not history:
        await callback.message.edit_text(
            "💬 " + _("history_empty", lang),
            reply_markup=main_menu_keyboard(lang),
            parse_mode="Markdown",
        )
        await callback.answer()
        return

    text = _("history_title", lang) + "\n\n"
    for i, entry in enumerate(history[-5:], 1):
        role_label = _("history_you", lang) if entry.get("role") == "user" else _("history_bot", lang)
        content = entry.get("content", "")[:100]
        text += f"{i}. {role_label}: {content}...\n\n"

    text += "\n" + _("history_footer", lang)
    await callback.message.edit_text(
        text, reply_markup=main_menu_keyboard(lang), parse_mode="Markdown"
    )
    await callback.answer()
