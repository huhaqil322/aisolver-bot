from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards.common import main_menu_keyboard, pagination_keyboard
from app.services.memory import get_conversation_history

router = Router(name="history")


@router.callback_query(F.data == "history")
async def show_history(callback: CallbackQuery) -> None:
    user = callback.from_user
    if not user:
        return
    history = await get_conversation_history(user.id, limit=10)
    if not history:
        await callback.message.edit_text(
            "💬 **Conversation History**\n\nNo conversations yet. Start by solving a problem!",
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown",
        )
        await callback.answer()
        return

    text = "💬 **Recent Conversations**\n\n"
    for i, entry in enumerate(history[-5:], 1):
        role = "👤 You" if entry.get("role") == "user" else "🤖 Bot"
        content = entry.get("content", "")[:100]
        text += f"{i}. {role}: {content}...\n\n"

    text += "\nUse /solve to start a new conversation."
    await callback.message.edit_text(
        text, reply_markup=main_menu_keyboard(), parse_mode="Markdown"
    )
    await callback.answer()
