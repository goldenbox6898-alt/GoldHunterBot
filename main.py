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


# =========================
# تنظیمات ربات
# =========================

TOKEN = os.getenv("BOT_TOKEN")

CHANNEL = "@GoldHunter68980"

VIP_CHANNEL = -1004306822405

ADMIN_ID = 7913800180

DB = "users.db"

VIP_LINK = "https://t.me/+gPsx8C4YirZlMWY0"

DARYA_LINK = "https://daryagold.com/login?ref=GoldHunter"

REF_CODE = "99013"


# حافظه موقت سیگنال
SIGNAL_TYPE = {}
SIGNAL_TEXT = {}
# =========================
# ساخت دیتابیس
# =========================

def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        username TEXT,
        vip INTEGER DEFAULT 0,
        vip_end TEXT,
        plan TEXT,
        days INTEGER DEFAULT 0,
        invited_by INTEGER DEFAULT 0,
        invites INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


# =========================
# افزودن کاربر
# =========================

def add_user(user, inviter=None):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id FROM users WHERE user_id=?",
        (user.id,)
    )

    exists = cursor.fetchone()

    if not exists:

        cursor.execute(
            """
            INSERT INTO users(
                user_id,
                name,
                username,
                invited_by
            )
            VALUES(?,?,?,?)
            """,
            (
                user.id,
                user.first_name,
                user.username,
                inviter
            )
        )

        if inviter:
            cursor.execute(
                """
                UPDATE users
                SET invites=invites+1
                WHERE user_id=?
                """,
                (inviter,)
            )

    conn.commit()
    conn.close()
# =========================
# منوی اصلی
# =========================

def main_menu():
    keyboard = [
        ["📈 سیگنال VIP", "💎 خرید اشتراک"],
        ["👤 حساب کاربری", "👥 دعوت دوستان"],
        ["📚 آموزش‌ها", "☎️ پشتیبانی"],
        ["📢 مدیریت سیگنال"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# =========================
# استارت
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    inviter = None

    if context.args:
        try:
            inviter = int(context.args[0])

            if inviter == user.id:
                inviter = None

        except:
            inviter = None

    add_user(user, inviter)

    try:

        member = await context.bot.get_chat_member(
            CHANNEL,
            user.id
        )

    except:

        await update.message.reply_text(
            "❌ خطا در بررسی عضویت کانال"
        )
        return

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
            "❌ برای استفاده از ربات ابتدا عضو کانال شوید.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        return

    await update.message.reply_text(
        f"""🥇 Gold Hunter | شکارچی مظنه طلا 🏅

سلام {user.first_name} 🌹

✅ عضویت شما تایید شد.

یکی از گزینه‌های زیر را انتخاب کنید.""",
        reply_markup=main_menu(),
    )
# =========================
# تایید عضویت
# =========================

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    member = await context.bot.get_chat_member(
        CHANNEL,
        query.from_user.id
    )

    if member.status in ["left", "kicked"]:

        await query.edit_message_text(
            "❌ هنوز عضو کانال نیستید."
        )

        return

    await query.message.reply_text(
        "✅ عضویت شما تایید شد.",
        reply_markup=main_menu()
    )

    await query.delete_message()
# =========================
# دکمه‌های منو
# =========================

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    user = update.effective_user

    # خرید اشتراک
    if text == "💎 خرید اشتراک":

        keyboard = [
            [InlineKeyboardButton("📅 روزانه | 200 هزار", callback_data="plan_daily")],
            [InlineKeyboardButton("📅 هفتگی | 690 هزار", callback_data="plan_weekly")],
            [InlineKeyboardButton("📅 ماهانه | 1,890 میلیون", callback_data="plan_monthly")],
        ]

        await update.message.reply_text(
            "💎 نوع اشتراک را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # حساب کاربری
    elif text == "👤 حساب کاربری":

        await update.message.reply_text(
            f"""👤 حساب کاربری

🆔 آیدی:
{user.id}

👤 نام:
{user.first_name}

🤖 یوزرنیم:
@{user.username if user.username else "ندارد"}

💎 وضعیت اشتراک:
عادی"""
        )

    # دعوت دوستان
    elif text == "👥 دعوت دوستان":

        link = f"https://t.me/GoldHunterMazanhSignalBot?start={user.id}"

        await update.message.reply_text(
            f"""🎁 سیستم دعوت دوستان

🔗 لینک اختصاصی شما:

{link}

🌊 ثبت نام دریا گلد:
{DARYA_LINK}

🎁 کد معرف:
{REF_CODE}"""
        )

    # آموزش‌ها
    elif text == "📚 آموزش‌ها":

    await update.message.reply_text(
        "📚 بخش آموزش‌ها به‌زودی فعال می‌شود."
    )

elif text == "📢 مدیریت سیگنال":

    await signal_menu(update, context)

elif text == "☎️ پشتیبانی":

    await update.message.reply_text(
        "☎️ پشتیبانی\n\n@MazanhGoldAcademy"
    )
# =========================
# انتخاب پلن خرید
# =========================

async def plan_select(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    plan = query.data.replace("plan_", "")

    prices = {
        "daily": "200,000 تومان",
        "weekly": "690,000 تومان",
        "monthly": "1,890,000 تومان",
    }

    names = {
        "daily": "روزانه",
        "weekly": "هفتگی",
        "monthly": "ماهانه",
    }

    await query.message.reply_text(
        f"""💎 پلن انتخابی:

📦 {names[plan]}

💰 مبلغ:
{prices[plan]}

💳 شماره کارت:

6219 8619 0960 4646

👤 داود شکوری مقدم

📨 بعد از واریز، رسید پرداخت را به صورت عکس برای ربات ارسال کنید."""
    )
# =========================
# دریافت رسید پرداخت
# =========================

async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if not update.message.photo:
        return

    photo = update.message.photo[-1]

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ تایید پرداخت",
                callback_data=f"vip_{user.id}"
            ),
            InlineKeyboardButton(
                "❌ رد پرداخت",
                callback_data=f"reject_{user.id}"
            ),
        ]
    ]

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo.file_id,
        caption=f"""📩 رسید پرداخت جدید

👤 نام:
{user.first_name}

🆔 آیدی:
{user.id}

🤖 یوزرنیم:
@{user.username if user.username else "ندارد"}""",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text(
        "✅ رسید پرداخت شما ارسال شد.\n\nپس از تایید مدیریت، اشتراک شما فعال می‌شود."
    )
# =========================
# تایید یا رد پرداخت
# =========================

async def vip_action(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    user_id = int(data.split("_")[1])

    if data.startswith("vip_"):

        await context.bot.send_message(
            chat_id=user_id,
            text=f"""🎉 پرداخت شما تایید شد.

✅ اشتراک VIP شما فعال شد.

🔐 لینک کانال VIP:

{VIP_LINK}
"""
        )

        await query.edit_message_caption(
            caption="✅ پرداخت تایید شد."
        )

    elif data.startswith("reject_"):

        await context.bot.send_message(
            chat_id=user_id,
            text="""❌ پرداخت شما تایید نشد.

لطفاً با پشتیبانی تماس بگیرید."""
        )

        await query.edit_message_caption(
            caption="❌ پرداخت رد شد."
        )
# =========================
# مدیریت سیگنال
# =========================

async def signal_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        [
            InlineKeyboardButton("🟢 سیگنال خرید", callback_data="send_buy")
        ],
        [
            InlineKeyboardButton("🔴 سیگنال فروش", callback_data="send_sell")
        ],
    ]

    await update.message.reply_text(
        "📢 نوع سیگنال را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

app = Application.builder().token(TOKEN).build()

# دستورات
app.add_handler(CommandHandler("start", start))

# عضویت
app.add_handler(CallbackQueryHandler(check, pattern="^check$"))

# خرید اشتراک
app.add_handler(CallbackQueryHandler(plan_select, pattern="^plan_"))

# تایید پرداخت
app.add_handler(CallbackQueryHandler(vip_action, pattern="^(vip_|reject_)"))

# پیام‌های متنی
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        buttons
    ),
    group=0
)

# مدیریت سیگنال
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        receive_signal
    ),
    group=1
)

# دریافت رسید پرداخت
app.add_handler(
    MessageHandler(
        filters.PHOTO,
        receipt
    )
)

print("🤖 Gold Hunter Bot Started")

init_db()

app.run_polling()