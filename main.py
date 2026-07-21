from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@GoldHunter68980"


def main_menu():
    keyboard = [
        ["📈 سیگنال VIP", "💎 خرید اشتراک"],
        ["👤 حساب کاربری", "👥 دعوت دوستان"],
        ["📚 آموزش‌ها", "☎️ پشتیبانی"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    member = await context.bot.get_chat_member(CHANNEL, user.id)

    if member.status in ["left", "kicked"]:
        keyboard = [
            [
                InlineKeyboardButton(
                    "📢 عضویت در کانال",
                    url="https://t.me/GoldHunter68980",
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ عضو شدم",
                    callback_data="check",
                )
            ],
        ]

        await update.message.reply_text(
            "❌ برای استفاده از ربات ابتدا در کانال رسمی عضو شوید.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    await update.message.reply_text(
        f"""🥇 Gold Hunter | شکارچی مظنه طلا

سلام {user.first_name} 🌹

✅ عضویت شما تایید شد.

یکی از گزینه‌های زیر را انتخاب کنید.""",
        reply_markup=main_menu(),
    )


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    member = await context.bot.get_chat_member(
        CHANNEL,
        query.from_user.id,
    )

    if member.status in ["left", "kicked"]:
        await query.edit_message_text(
            "❌ هنوز عضو کانال نیستید."
        )
    else:
        await query.message.reply_text(
            f"""🥇 Gold Hunter | شکارچی مظنه طلا

سلام {query.from_user.first_name} 🌹

✅ عضویت شما تایید شد.

یکی از گزینه‌های زیر را انتخاب کنید.""",
            reply_markup=main_menu(),
        )

        await query.delete_message()

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💎 خرید اشتراک":
        await update.message.reply_text(
            """💎 خرید اشتراک VIP

📅 روزانه
200,000 تومان

📅 هفتگی
690,000 تومان

📅 ماهانه
1,890,000 تومان

💳 شماره کارت:

6219 8619 0960 4646

👤 داود شکوری مقدم

📨 ارسال رسید:
@MazanhGoldAcademy"""
        )

    elif text == "☎️ پشتیبانی":
        await update.message.reply_text(
            "☎️ پشتیبانی\n\n@MazanhGoldAcademy"
        )
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(
    CallbackQueryHandler(check, pattern="check")
)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buttons))
app.run_polling()