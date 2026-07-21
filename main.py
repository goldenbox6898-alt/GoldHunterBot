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
import sqlite3
from datetime import datetime, timedelta
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@GoldHunter68980"
DB = "users.db"
ADMIN_ID = 7913800180
VIP_LINK = "https://t.me/+gPsx8C4YirZlMWY0"

def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        username TEXT,
        vip INTEGER DEFAULT 0,
        vip_end TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_user(user):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO users
    (user_id, name, username)
    VALUES (?, ?, ?)
    """,
    (
        user.id,
        user.first_name,
        user.username
    ))

    conn.commit()
    conn.close()

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
    add_user(user)
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

✅ عضویت شما تایید شد.""",
            reply_markup=main_menu(),
        )

        await query.delete_message()


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    user = update.effective_user


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


    elif text == "👤 حساب کاربری":

        await update.message.reply_text(
            f"""👤 حساب کاربری

🆔 آیدی:
{user.id}

👤 نام:
{user.first_name}

💎 وضعیت اشتراک:
عادی

🤖 یوزرنیم:
@{user.username if user.username else "ندارد"}"""
        )


    elif text == "☎️ پشتیبانی":

        await update.message.reply_text(
            "☎️ پشتیبانی\n\n@MazanhGoldAcademy"
        )
async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    photo = update.message.photo[-1]

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo.file_id,
        caption=f"""📩 رسید جدید VIP

👤 نام:
{user.first_name}

🆔 آیدی:
{user.id}

🤖 یوزرنیم:
@{user.username if user.username else "ندارد"}"""
    )

    await update.message.reply_text(
        "✅ رسید شما ارسال شد.\nپس از بررسی مدیریت، اشتراک فعال می‌شود."
    )
init_db()
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    CallbackQueryHandler(check, pattern="check")
)

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, buttons)
)

app.run_polling()