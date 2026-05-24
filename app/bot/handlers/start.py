from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards.common import main_menu_keyboard, help_keyboard
from app.services.memory import get_user_context

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user = message.from_user
    if not user:
        return
    context = await get_user_context(user)
    welcome_text = (
        f"Hello, {user.first_name or 'there'}! 👋\n\n"
        f"I am an advanced AI solver bot. I can help you with:\n"
        f"• Mathematics & Olympiad problems\n"
        f"• Physics, Chemistry, Programming\n"
        f"• Image analysis with OCR\n"
        f"• Step-by-step explanations\n\n"
        f"Select an option below to get started:"
    )
    await message.answer(welcome_text, reply_markup=main_menu_keyboard())


@router.message(Command("help"))
@router.callback_query(F.data == "help")
async def cmd_help(event: Message | CallbackQuery) -> None:
    text = (
        "🤖 **AI Solver Bot Help**\n\n"
        "**Commands:**\n"
        "/start - Start the bot\n"
        "/solve <problem> - Solve a problem\n"
        "/help - Show this help\n"
        "/profile - Your profile & stats\n"
        "/premium - Premium plans\n\n"
        "**How to use:**\n"
        "1. Type or paste your problem\n"
        "2. Upload an image of the problem\n"
        "3. Select a subject for better results\n\n"
        "**Supported:** Math, Physics, Chemistry, Programming, and more!"
    )
    if isinstance(event, Message):
        await event.answer(text, reply_markup=help_keyboard(), parse_mode="Markdown")
    else:
        await event.message.edit_text(text, reply_markup=help_keyboard(), parse_mode="Markdown")


@router.callback_query(F.data == "menu")
async def go_to_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Main Menu - Select an option:",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Action cancelled. Returning to menu.",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()
