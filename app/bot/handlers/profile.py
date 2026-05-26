from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards.common import profile_keyboard, settings_keyboard, main_menu_keyboard
from app.services.memory import get_user_context

router = Router(name="profile")


@router.message(Command("profile"))
@router.callback_query(F.data == "profile")
async def cmd_profile(event: Message | CallbackQuery) -> None:
    user = event.from_user
    if not user:
        return
    context = await get_user_context(user)

    text = (
        f"👤 **Your Profile**\n\n"
        f"ID: `{user.id}`\n"
        f"Username: @{user.username or 'N/A'}\n"
        f"Status: 🆓 Active\n"
        f"Language: {user.language_code or 'en'}\n\n"
        f"📊 **Statistics:**\n"
        f"Total requests: {context.get('total_requests', 0)}\n"
        f"Today: {context.get('daily_requests', 0)}\n"
        f"Tokens used: {context.get('total_tokens', 0)}\n\n"
        f"📅 Joined: {context.get('created_at', 'N/A')}"
    )

    if isinstance(event, Message):
        await event.answer(text, reply_markup=profile_keyboard(), parse_mode="Markdown")
    else:
        await event.message.edit_text(text, reply_markup=profile_keyboard(), parse_mode="Markdown")
        await event.answer()


@router.callback_query(F.data == "profile:stats")
async def profile_stats(callback: CallbackQuery) -> None:
    user = callback.from_user
    if not user:
        return
    context = await get_user_context(user)
    await callback.message.edit_text(
        f"📊 **Detailed Stats**\n\n"
        f"• Total Requests: {context.get('total_requests', 0)}\n"
        f"• Daily Requests: {context.get('daily_requests', 0)}\n"
        f"• Monthly Tokens: {context.get('monthly_tokens', 0)}\n"
        f"• Total Tokens: {context.get('total_tokens', 0)}\n"
        f"• Conversations: {context.get('conversations_count', 0)}\n"
        f"• Referrals: {context.get('referral_count', 0)}\n\n"
        f"⚡ Daily limit: {context.get('daily_limit', 20)}\n"
        f"📅 Monthly limit: {context.get('monthly_limit', 100000)}",
        reply_markup=profile_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "profile:settings")
async def profile_settings(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "⚙️ **Settings**\n\n"
        "Customize your experience:",
        reply_markup=settings_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "profile:reset")
async def profile_reset(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "✅ Daily usage has been reset.",
        reply_markup=profile_keyboard(),
    )
    await callback.answer()
