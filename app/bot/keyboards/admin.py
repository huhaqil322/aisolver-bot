from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Dashboard", callback_data="admin:dashboard")
    builder.button(text="👥 Users", callback_data="admin:users")
    builder.button(text="📈 Analytics", callback_data="admin:analytics")
    builder.button(text="🔔 Broadcast", callback_data="admin:broadcast")
    builder.button(text="⚙️ Settings", callback_data="admin:settings")
    builder.button(text="📋 Logs", callback_data="admin:logs")
    builder.button(text="🚫 Bans", callback_data="admin:bans")
    builder.adjust(2, 2, 2, 2)
    return builder.as_markup()


def admin_user_actions_keyboard(user_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Ban", callback_data=f"admin:ban:{user_id}")
    builder.button(text="Unban", callback_data=f"admin:unban:{user_id}")
    builder.button(text="Make Admin", callback_data=f"admin:make_admin:{user_id}")
    builder.button(text="Remove Admin", callback_data=f"admin:remove_admin:{user_id}")
    builder.button(text="Add tokens", callback_data=f"admin:add_tokens:{user_id}")
    builder.button(text="↩ Back", callback_data="admin:users")
    builder.adjust(2, 2, 2)
    return builder.as_markup()


def admin_broadcast_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Send Message", callback_data="admin:broadcast:send")
    builder.button(text="✅ Confirm Broadcast", callback_data="admin:broadcast:confirm")
    builder.button(text="❌ Cancel", callback_data="admin:dashboard")
    builder.adjust(1, 2)
    return builder.as_markup()
