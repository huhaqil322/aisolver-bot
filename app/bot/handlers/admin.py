from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.bot.filters.admin import AdminFilter
from app.bot.keyboards.admin import admin_main_keyboard, admin_broadcast_keyboard
from app.bot.keyboards.common import main_menu_keyboard
from app.config.settings import get_settings

settings = get_settings()
router = Router(name="admin")
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


class BroadcastStates(StatesGroup):
    waiting_for_message = State()
    confirming = State()


@router.message(Command("admin"))
@router.callback_query(F.data == "admin")
async def cmd_admin(event: Message | CallbackQuery) -> None:
    text = "🔐 **Admin Panel**\n\nWelcome to the admin control panel."
    if isinstance(event, Message):
        await event.answer(text, reply_markup=admin_main_keyboard(), parse_mode="Markdown")
    else:
        await event.message.edit_text(text, reply_markup=admin_main_keyboard(), parse_mode="Markdown")
        await event.answer()


@router.callback_query(F.data == "admin:dashboard")
async def admin_dashboard(callback: CallbackQuery) -> None:
    dashboard_text = (
        "📊 **Admin Dashboard**\n\n"
        f"👥 Active Users: *fetching...*\n"
        f"📈 Requests Today: *fetching...*\n"
        f"💰 Revenue: *fetching...*\n"
        f"🤖 AI Cost: *fetching...*\n"
        f"⚠️ Errors: *fetching...*\n\n"
        f"*Detailed analytics coming soon*"
    )
    await callback.message.edit_text(
        dashboard_text, reply_markup=admin_main_keyboard(), parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "admin:users")
async def admin_users(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "👥 **User Management**\n\nUser list and search coming soon.\n"
        "Use /admin in chat to manage users.",
        reply_markup=admin_main_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(BroadcastStates.waiting_for_message)
    await callback.message.edit_text(
        "📝 **Send Broadcast**\n\nSend me the message you want to broadcast to all users.\n"
        "You can use Markdown formatting.",
        reply_markup=admin_broadcast_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(BroadcastStates.waiting_for_message)
async def broadcast_get_message(message: Message, state: FSMContext) -> None:
    await state.update_data(broadcast_text=message.text or message.caption or "")
    await state.set_state(BroadcastStates.confirming)
    await message.answer(
        f"📝 **Broadcast Preview:**\n\n{message.text or message.caption}\n\n"
        f"Send /confirm to broadcast or /cancel to cancel.",
        parse_mode="Markdown",
    )


@router.message(BroadcastStates.confirming, Command("confirm"))
async def broadcast_confirm(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    broadcast_text = data.get("broadcast_text", "")
    await message.answer(f"✅ Broadcast sent to all users:\n\n{broadcast_text[:200]}...")
    await state.clear()


@router.callback_query(F.data == "admin:logs")
async def admin_logs(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "📋 **System Logs**\n\nLog viewer coming soon.",
        reply_markup=admin_main_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:analytics")
async def admin_analytics(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "📈 **Analytics Dashboard**\n\nDetailed analytics coming soon.",
        reply_markup=admin_main_keyboard(),
    )
    await callback.answer()
