from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.models.conversation import Subject


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🧮 Solve Problem", callback_data="solve")
    builder.button(text="📸 Upload Image", callback_data="image")
    builder.button(text="💬 History", callback_data="history")
    builder.button(text="👤 Profile", callback_data="profile")
    builder.button(text="❓ Help", callback_data="help")
    builder.adjust(2, 2)
    return builder.as_markup()


def subject_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    subjects = [
        ("Mathematics", Subject.MATHEMATICS.value),
        ("Physics", Subject.PHYSICS.value),
        ("Chemistry", Subject.CHEMISTRY.value),
        ("Programming", Subject.PROGRAMMING.value),
        ("General", Subject.GENERAL.value),
    ]
    for label, value in subjects:
        builder.button(text=label, callback_data=f"subject:{value}")
    builder.button(text="↩ Back", callback_data="menu")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Cancel", callback_data="cancel")
    return builder.as_markup()


def confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Confirm", callback_data=f"confirm:{action}")
    builder.button(text="❌ Cancel", callback_data="cancel")
    builder.adjust(2)
    return builder.as_markup()


def profile_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Stats", callback_data="profile:stats")
    builder.button(text="🔄 Reset Daily", callback_data="profile:reset")
    builder.button(text="⚙️ Settings", callback_data="profile:settings")
    builder.button(text="↩ Menu", callback_data="menu")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def settings_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🌐 Language", callback_data="settings:language")
    builder.button(text="📚 Explanation Level", callback_data="settings:level")
    builder.button(text="🤖 AI Provider", callback_data="settings:provider")
    builder.button(text="↩ Profile", callback_data="profile")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def help_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 How to Use", callback_data="help:usage")
    builder.button(text="📚 Supported Subjects", callback_data="help:subjects")
    builder.button(text="💡 Tips", callback_data="help:tips")
    builder.button(text="↩ Menu", callback_data="menu")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def pagination_keyboard(prefix: str, page: int, total: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if page > 0:
        builder.button(text="◀ Prev", callback_data=f"{prefix}:page:{page - 1}")
    if page < total - 1:
        builder.button(text="Next ▶", callback_data=f"{prefix}:page:{page + 1}")
    builder.button(text="↩ Back", callback_data="menu")
    builder.adjust(2 if (page > 0 and page < total - 1) else 1, 1)
    return builder.as_markup()
