from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery, SuccessfulPayment

from app.bot.keyboards.common import subscription_keyboard, main_menu_keyboard
from app.config.settings import get_settings
from app.services.memory import get_user_context

settings = get_settings()
router = Router(name="payments")

PREMIUM_PRICES = {
    "monthly": LabeledPrice(label="Premium Monthly", amount=999),
    "yearly": LabeledPrice(label="Premium Yearly", amount=7999),
    "enterprise": LabeledPrice(label="Enterprise", amount=29999),
}


@router.message(Command("premium"))
@router.callback_query(F.data == "premium")
async def cmd_premium(event: Message | CallbackQuery) -> None:
    text = (
        "⭐ **Premium Plans**\n\n"
        "**Free Tier:**\n"
        "• 20 requests/day\n"
        "• 100K tokens/month\n"
        "• Basic models\n\n"
        "**Premium Monthly — $9.99**\n"
        "• 500 requests/day\n"
        "• 5M tokens/month\n"
        "• All AI models\n"
        "• Priority support\n"
        "• No ads\n\n"
        "**Premium Yearly — $79.99**\n"
        "• All Premium features\n"
        "• 2 months free\n\n"
        "**Enterprise — $299.99**\n"
        "• Unlimited requests\n"
        "• Dedicated support\n"
        "• Custom models\n"
        "• Team access"
    )
    if isinstance(event, Message):
        await event.answer(text, reply_markup=subscription_keyboard(), parse_mode="Markdown")
    else:
        await event.message.edit_text(text, reply_markup=subscription_keyboard(), parse_mode="Markdown")
        await event.answer()


@router.callback_query(F.data.startswith("subscribe:"))
async def process_subscription(callback: CallbackQuery) -> None:
    if not settings.payments_enabled or not settings.payment_provider_token:
        await callback.message.edit_text(
            "Payments are currently unavailable. Please try again later.",
            reply_markup=main_menu_keyboard(),
        )
        await callback.answer()
        return

    parts = callback.data.split(":")
    plan = parts[1]
    duration = parts[2] if len(parts) > 2 else "monthly"

    price_key = f"{plan}_{duration}" if plan == "premium" else plan
    prices = [PREMIUM_PRICES.get(duration, PREMIUM_PRICES["monthly"])]

    await callback.message.answer_invoice(
        title=f"{plan.capitalize()} {duration.capitalize()}",
        description=f"AI Solver Bot {plan.capitalize()} Subscription - {duration.capitalize()}",
        provider_token=settings.payment_provider_token,
        currency="USD",
        prices=prices,
        payload=f"{plan}_{duration}",
        start_parameter="subscription",
    )
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout: PreCheckoutQuery) -> None:
    await pre_checkout.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message) -> None:
    payment = message.successful_payment
    if not payment:
        return
    await message.answer(
        f"✅ **Payment Successful!**\n\n"
        f"Amount: ${payment.total_amount / 100:.2f}\n"
        f"Plan: {payment.invoice_payload}\n\n"
        f"Your premium features are now active. Enjoy! 🎉",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown",
    )
