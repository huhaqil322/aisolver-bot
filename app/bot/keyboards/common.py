from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.models.conversation import Subject
from app.utils.i18n import _


def main_menu_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("btn_solve", lang), callback_data="solve")
    builder.button(text=_("btn_image", lang), callback_data="image")
    builder.button(text=_("btn_history", lang), callback_data="history")
    builder.button(text=_("btn_profile", lang), callback_data="profile")
    builder.button(text=_("btn_help", lang), callback_data="help")
    builder.adjust(2, 2)
    return builder.as_markup()


def subject_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    subjects = [
        (_("subject_mathematics", lang), Subject.MATHEMATICS.value),
        (_("subject_physics", lang), Subject.PHYSICS.value),
        (_("subject_chemistry", lang), Subject.CHEMISTRY.value),
        (_("subject_programming", lang), Subject.PROGRAMMING.value),
        (_("subject_general", lang), Subject.GENERAL.value),
    ]
    for label, value in subjects:
        builder.button(text=label, callback_data=f"subject:{value}")
    builder.button(text=_("btn_back", lang), callback_data="menu")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()


def cancel_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("btn_cancel", lang), callback_data="cancel")
    return builder.as_markup()


def confirmation_keyboard(action: str, lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("btn_confirm", lang), callback_data=f"confirm:{action}")
    builder.button(text=_("btn_cancel", lang), callback_data="cancel")
    builder.adjust(2)
    return builder.as_markup()


def profile_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("btn_stats", lang), callback_data="profile:stats")
    builder.button(text=_("btn_reset", lang), callback_data="profile:reset")
    builder.button(text=_("btn_settings", lang), callback_data="profile:settings")
    builder.button(text=_("btn_menu", lang), callback_data="menu")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def settings_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("btn_language", lang), callback_data="settings:language")
    builder.button(text=_("btn_level", lang), callback_data="settings:level")
    builder.button(text=_("btn_provider", lang), callback_data="settings:provider")
    builder.button(text=_("btn_menu", lang), callback_data="profile")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def help_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("btn_usage", lang), callback_data="help:usage")
    builder.button(text=_("btn_subjects", lang), callback_data="help:subjects")
    builder.button(text=_("btn_tips", lang), callback_data="help:tips")
    builder.button(text=_("btn_menu", lang), callback_data="menu")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def pagination_keyboard(prefix: str, page: int, total: int, lang: str = "en") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if page > 0:
        builder.button(text=_("btn_prev", lang), callback_data=f"{prefix}:page:{page - 1}")
    if page < total - 1:
        builder.button(text=_("btn_next", lang), callback_data=f"{prefix}:page:{page + 1}")
    builder.button(text=_("btn_back", lang), callback_data="menu")
    builder.adjust(2 if (page > 0 and page < total - 1) else 1, 1)
    return builder.as_markup()
