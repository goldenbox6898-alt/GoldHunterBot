from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@GoldHunter68980"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    member = await context.bot.get_chat_member(CHANNEL, user.id)

    if member.status in ["left", "kicked"]:
        keyboard = [
            [InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/GoldHunter68980")],
            [InlineKeyboardButton("✅ عضو شدم", callback_data="check")]
        ]

        await update.message.reply_text(
            "❌ برای استفاده از ربات ابتدا در کانال رسمی عضو شوید.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await update.message.reply_text(
        "🥇 به ربات رسمی Gold Hunter خوش آمدید.\n\n✅ عضویت شما تایید شد."
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    member = await context.bot.get_chat_member(CHANNEL, query.from_user.id)

    if member.status in ["left", "kicked"]:
        await query.edit_message_text("❌ هنوز عضو کانال نیستید.")
    else:
        await query.edit_message_text(
            "🎉 عضویت شما تایید شد.\n\nبه ربات Gold Hunter خوش آمدید."
        )

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check, pattern="check"))

app.run_polling()