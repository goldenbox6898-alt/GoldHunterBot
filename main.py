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


#=========================
# تنظیمات
#=========================

TOKEN = os.getenv("BOT_TOKEN")

CHANNEL = "@GoldHunter68980"

VIP_CHANNEL = -1004306822405

ADMIN_ID = 7913800180

DB = "users.db"

VIP_LINK = "https://t.me/+gPsx8C4YirZlMWY0"

DARYA_LINK = "https://daryagold.com/login?ref=GoldHunter"

REF_CODE = "99013"


PLANS = {
    "daily": {
        "name": "روزانه",
        "days": 1,
        "price": "200,000 تومان",
    },

    "weekly": {
        "name": "هفتگی",
        "days": 7,
        "price": "690,000 تومان",
    },

    "monthly": {
        "name": "ماهانه",
        "days": 30,
        "price": "1,890,000 تومان",
    },
}


#=========================
# دیتابیس
#=========================

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

        days INTEGER

    )
    """)

    conn.commit()
    conn.close()


def add_user(user):

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO users
    (user_id,name,username)
    VALUES(?,?,?)
    """,
    (
        user.id,
        user.first_name,
        user.username
    ))

    conn.commit()
    conn.close()


def save_plan(user_id, plan):

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET plan=?,days=?
    WHERE user_id=?
    """,
    (
        plan,
        PLANS[plan]["days"],
        user_id
    ))

    conn.commit()
    conn.close()


def activate_vip(user_id):

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT days FROM users WHERE user_id=?",
        (user_id,)
    )

    result = cursor.fetchone()

    days = result[0] if result else 1

    end = datetime.now() + timedelta(days=days)

    cursor.execute("""
    UPDATE users
    SET vip=1,
        vip_end=?
    WHERE user_id=?
    """,
    (
        end.strftime("%Y-%m-%d"),
        user_id
    ))

    conn.commit()
    conn.close()


#=========================
# منوی اصلی
#=========================

def main_menu():

    keyboard = [

        ["📈 سیگنال VIP", "💎 خرید اشتراک"],

        ["👤 حساب کاربری", "👥 دعوت دوستان"],

        ["📚 آموزش‌ها", "☎️ پشتیبانی"],

    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


#=========================
# استارت
#=========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    add_user(user)

    member = await context.bot.get_chat_member(
        CHANNEL,
        user.id
    )

    if member.status in ["left", "kicked"]:

        keyboard = [

            [
                InlineKeyboardButton(
                    "📢 عضویت در کانال",
                    url="https://t.me/GoldHunter68980"
                )
            ],

            [
                InlineKeyboardButton(
                    "✅ عضو شدم",
                    callback_data="check"
                )
            ]

        ]

        await update.message.reply_text(
            "❌ برای استفاده از ربات ابتدا در کانال رسمی عضو شوید.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    await update.message.reply_text(
        f"""🥇 Gold Hunter | شکارچی مظنه طلا

سلام {user.first_name} 🌹

✅ عضویت شما تایید شد.

یکی از گزینه‌های زیر را انتخاب کنید.""",
        reply_markup=main_menu()
    )


#=========================
# بررسی عضویت
#=========================

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
#=========================
# دکمه‌های منو
#=========================

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    user = update.effective_user

    # =========================
    # سیگنال VIP
    # =========================

    if text == "📈 سیگنال VIP":

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT vip,vip_end FROM users WHERE user_id=?",
            (user.id,)
        )

        data = cursor.fetchone()

        conn.close()

        if data and data[0] == 1:

            end = data[1]

            if end >= datetime.now().strftime("%Y-%m-%d"):

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "🔐 ورود به کانال VIP",
                            url=VIP_LINK
                        )
                    ]
                ]

                await update.message.reply_text(
                    f"""✅ اشتراک VIP شما فعال است.

📅 پایان اشتراک:
{end}

برای ورود روی دکمه زیر کلیک کنید.""",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

            else:

                await update.message.reply_text(
                    "⛔ اشتراک شما منقضی شده است.\n\nبرای تمدید روی «💎 خرید اشتراک» بزنید."
                )

        else:

            await update.message.reply_text(
                "⛔ شما اشتراک VIP ندارید.\n\nبرای دریافت سیگنال ابتدا اشتراک تهیه کنید."
            )

    # =========================
    # خرید اشتراک
    # =========================

    elif text == "💎 خرید اشتراک":

        keyboard = [

            [
                InlineKeyboardButton(
                    "📅 روزانه | 200,000",
                    callback_data="plan_daily"
                )
            ],

            [
                InlineKeyboardButton(
                    "📅 هفتگی | 690,000",
                    callback_data="plan_weekly"
                )
            ],

            [
                InlineKeyboardButton(
                    "📅 ماهانه | 1,890,000",
                    callback_data="plan_monthly"
                )
            ]

        ]

        await update.message.reply_text(
            "💎 یکی از پلن‌های زیر را انتخاب کنید.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # =========================
    # حساب کاربری
    # =========================

    elif text == "👤 حساب کاربری":

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT vip,vip_end FROM users WHERE user_id=?",
            (user.id,)
        )

        data = cursor.fetchone()

        conn.close()

        status = "عادی"
        end = "-"

        if data and data[0] == 1:
            status = "VIP"
            end = data[1]

        await update.message.reply_text(
            f"""👤 حساب کاربری

🆔 آیدی:
{user.id}

👤 نام:
{user.first_name}

🤖 یوزرنیم:
@{user.username if user.username else "ندارد"}

💎 وضعیت اشتراک:
{status}

📅 پایان اشتراک:
{end}"""
        )

    # =========================
    # دعوت دوستان
    # =========================

    elif text == "👥 دعوت دوستان":

        keyboard = [

            [
                InlineKeyboardButton(
                    "🥇 کانال رسمی Gold Hunter",
                    url="https://t.me/GoldHunter68980"
                )
            ],

            [
                InlineKeyboardButton(
                    "💰 ثبت‌نام در دریا گلد",
                    url=DARYA_LINK
                )
            ]

        ]

        await update.message.reply_text(
            f"""👥 دوستانت را دعوت کن.

🥇 کانال رسمی:
https://t.me/GoldHunter68980

💰 ثبت‌نام در دریا گلد

🆔 کد معرف:
{REF_CODE}

با ثبت‌نام از طریق لینک بالا، کد معرف به صورت خودکار ثبت می‌شود.""",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # =========================
    # آموزش‌ها
    # =========================

    elif text == "📚 آموزش‌ها":

        await update.message.reply_text(
            """📚 آموزش‌های Gold Hunter

به‌زودی آموزش‌های اختصاصی اسمارت مانی، ICT، مدیریت سرمایه و روانشناسی معامله در این بخش قرار می‌گیرد."""
        )

    # =========================
    # پشتیبانی
    # =========================

    elif text == "☎️ پشتیبانی":

        await update.message.reply_text(
            "☎️ ارتباط با پشتیبانی:\n\n@MazanhGoldAcademy"
        )
#=========================
# انتخاب پلن
#=========================

async def plan_select(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    plan = query.data.replace("plan_", "")

    save_plan(
        query.from_user.id,
        plan
    )

    await query.message.reply_text(
        f"""💎 پلن انتخاب شد

📦 نوع اشتراک:
{PLANS[plan]["name"]}

💰 مبلغ:
{PLANS[plan]["price"]}

💳 شماره کارت:

6219 8619 0960 4646

👤 داود شکوری مقدم

📸 لطفاً پس از پرداخت، عکس رسید را برای ربات ارسال کنید."""
    )


#=========================
# دریافت رسید
#=========================

async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    photo = update.message.photo[-1]

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT plan FROM users WHERE user_id=?",
        (user.id,)
    )

    result = cursor.fetchone()

    conn.close()

    plan_name = "نامشخص"

    if result and result[0] in PLANS:
        plan_name = PLANS[result[0]]["name"]

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ تایید",
                callback_data=f"vip_{user.id}"
            ),
            InlineKeyboardButton(
                "❌ رد",
                callback_data=f"reject_{user.id}"
            )
        ]
    ]

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo.file_id,
        caption=f"""📩 رسید جدید

👤 نام:
{user.first_name}

🆔 آیدی:
{user.id}

🤖 یوزرنیم:
@{user.username if user.username else "ندارد"}

📦 پلن:
{plan_name}""",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text(
        "✅ رسید شما ارسال شد.\n\nپس از تایید مدیریت، اشتراک فعال خواهد شد."
    )


#=========================
# تایید یا رد مدیر
#=========================

async def vip_action(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data

    user_id = int(data.split("_")[1])


    if data.startswith("vip_"):

        activate_vip(user_id)

        await context.bot.send_message(
            chat_id=user_id,
            text=f"""🎉 پرداخت شما تایید شد.

✅ اشتراک VIP فعال گردید.

🔐 لینک ورود به کانال VIP:
{VIP_LINK}
"""
        )


    elif data.startswith("reject_"):

        await context.bot.send_message(
            chat_id=user_id,
            text="""❌ پرداخت شما رد شد.

لطفاً با پشتیبانی تماس بگیرید."""
        )


#=========================
# حذف کاربران منقضی
#=========================
=======================
# حذف کاربران منقضی
#=========================

async def remove_expired_users(context: ContextTypes.DEFAULT_TYPE):

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        """
        SELECT user_id
        FROM users
        WHERE vip=1 AND vip_end < ?
        """,
        (today,)
    )

    users = cursor.fetchall()

    for user in users:

        try:

            await context.bot.ban_chat_member(
                chat_id=VIP_CHANNEL,
                user_id=user[0]
            )

            await context.bot.unban_chat_member(
                chat_id=VIP_CHANNEL,
                user_id=user[0]
            )

        except Exception:
            pass

        cursor.execute(
            """
            UPDATE users
            SET vip=0
            WHERE user_id=?
            """,
            (user[0],)
        )

    conn.commit()
    conn.close()


#=========================
# اجرای ربات
#=========================

init_db()

app = Application.builder().token(TOKEN).build()


app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

app.add_handler(
    CallbackQueryHandler(
        check,
        pattern="^check$"
    )
)

app.add_handler(
    CallbackQueryHandler(
        plan_select,
        pattern="^plan_"
    )
)

app.add_handler(
    CallbackQueryHandler(
        vip_action,
        pattern="^(vip_|reject_)"
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        buttons
    )
)

app.add_handler(
    MessageHandler(
        filters.PHOTO,
        receipt
    )
)

app.run_polling()