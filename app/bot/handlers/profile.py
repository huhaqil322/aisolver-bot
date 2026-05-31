from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards.common import profile_keyboard, settings_keyboard
from app.services.memory import get_user_context
from app.utils.i18n import _, resolve_lang

router = Router(name="profile")


@router.message(Command("profile"))
@router.callback_query(F.data == "profile")
async def cmd_profile(event: Message | CallbackQuery) -> None:
    user = event.from_user
    if not user:
        return
    lang = resolve_lang(user.language_code)
    context = await get_user_context(user)

    text = _("profile_title", lang,
             id=user.id,
             username=user.username or _("n_a", lang),
             language=user.language_code or "en",
             total_requests=context.get("total_requests", 0),
             daily_requests=context.get("daily_requests", 0),
             total_tokens=context.get("total_tokens", 0),
             created_at=context.get("created_at", _("n_a", lang)))

    if isinstance(event, Message):
        await event.answer(text, reply_markup=profile_keyboard(lang), parse_mode="Markdown")
    else:
        await event.message.edit_text(text, reply_markup=profile_keyboard(lang), parse_mode="Markdown")
        await event.answer()


@router.callback_query(F.data == "profile:stats")
async def profile_stats(callback: CallbackQuery) -> None:
    user = callback.from_user
    if not user:
        return
    lang = resolve_lang(user.language_code)
    context = await get_user_context(user)

    text = _("stats_title", lang,
             total_requests=context.get("total_requests", 0),
             daily_requests=context.get("daily_requests", 0),
             monthly_tokens=context.get("monthly_tokens", 0),
             total_tokens=context.get("total_tokens", 0),
             conversations_count=context.get("conversations_count", 0),
             referral_count=context.get("referral_count", 0),
             daily_limit=context.get("daily_limit", 20),
             monthly_limit=context.get("monthly_limit", 100000))

    await callback.message.edit_text(
        text,
        reply_markup=profile_keyboard(lang),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "profile:settings")
async def profile_settings(callback: CallbackQuery) -> None:
    lang = resolve_lang(callback.from_user.language_code if callback.from_user else None)
    await callback.message.edit_text(
        _("settings_title", lang),
        reply_markup=settings_keyboard(lang),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "profile:reset")
async def profile_reset(callback: CallbackQuery) -> None:
    lang = resolve_lang(callback.from_user.language_code if callback.from_user else None)
    await callback.message.edit_text(
        _("daily_reset", lang),
        reply_markup=profile_keyboard(lang),
    )
    await callback.answer()
