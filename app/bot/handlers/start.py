from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards.common import help_keyboard, main_menu_keyboard
from app.services.memory import get_user_context
from app.utils.i18n import _, resolve_lang

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user = message.from_user
    if not user:
        return
    await get_user_context(user)
    lang = resolve_lang(user.language_code)
    welcome_text = _("welcome", lang, name=user.first_name or "there")
    await message.answer(welcome_text, reply_markup=main_menu_keyboard(lang))


@router.message(Command("help"))
@router.callback_query(F.data == "help")
async def cmd_help(event: Message | CallbackQuery) -> None:
    lang = resolve_lang(event.from_user.language_code if event.from_user else None)
    text = _("help", lang)
    if isinstance(event, Message):
        await event.answer(text, reply_markup=help_keyboard(lang), parse_mode="Markdown")
    else:
        await event.message.edit_text(text, reply_markup=help_keyboard(lang), parse_mode="Markdown")


@router.callback_query(F.data == "menu")
async def go_to_menu(callback: CallbackQuery) -> None:
    lang = resolve_lang(callback.from_user.language_code if callback.from_user else None)
    await callback.message.edit_text(
        _("main_menu", lang),
        reply_markup=main_menu_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery) -> None:
    lang = resolve_lang(callback.from_user.language_code if callback.from_user else None)
    await callback.message.edit_text(
        _("action_cancelled", lang),
        reply_markup=main_menu_keyboard(lang),
    )
    await callback.answer()
