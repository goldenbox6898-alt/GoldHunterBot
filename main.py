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
VIP_CHANNEL = -1004306822405

DB = "users.db"

ADMIN_ID = 7913800180

VIP_LINK = "https://t.me/+gPsx8C4YirZlMWY0"


PLANS = {
    "daily": {
        "name": "روزانه",
        "days": 1,
        "price": "200,000 تومان"
    },
    "weekly": {
        "name": "هفتگی",
        "days": 7,
        "price": "690,000 تومان"
    },
    "monthly": {
        "name": "ماهانه",
        "days": 30,
        "price": "1,890,000 تومان"
    }
}


def init_db():

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (

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
    VALUES (?,?,?)
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
    SET plan=?, days=?
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

    end_date = datetime.now() + timedelta(days=days)

    cursor.execute("""
    UPDATE users
    SET vip=1, vip_end=?
    WHERE user_id=?
    """,
    (
        end_date.strftime("%Y-%m-%d"),
        user_id
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
        resize_keyboard=True
    )



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
            "❌ ابتدا عضو کانال رسمی شوید.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return


    await update.message.reply_text(
        f"""🥇 Gold Hunter | شکارچی مظنه طلا

سلام {user.first_name} 🌹

✅ عضویت تایید شد.""",
        reply_markup=main_menu()
    )



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

    else:

        await query.message.reply_text(
            "✅ عضویت تایید شد.",
            reply_markup=main_menu()
        )

        await query.delete_message()



async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    user = update.effective_user
if text == "📈 سیگنال VIP":

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT vip, vip_end FROM users WHERE user_id=?",
        (user.id,)
    )

    data = cursor.fetchone()

    conn.close()


    if data and data[0] == 1:

        end = data[1]

        if end >= datetime.now().strftime("%Y-%m-%d"):

            await update.message.reply_text(
                f"""✅ اشتراک VIP شما فعال است.

🔐 ورود به کانال VIP:

{VIP_LINK}

📅 پایان اشتراک:
{end}"""
            )

        else:

            await update.message.reply_text(
                """⛔ اشتراک VIP شما به پایان رسیده.

برای تمدید:
💎 خرید اشتراک"""
            )

    else:

        await update.message.reply_text(
            """⛔ شما اشتراک VIP ندارید.

برای دریافت سیگنال:
💎 خرید اشتراک"""
        )

    return

    if text == "💎 خرید اشتراک":

        keyboard = [
            [
                InlineKeyboardButton(
                    "📅 روزانه - 200,000",
                    callback_data="plan_daily"
                )
            ],
            [
                InlineKeyboardButton(
                    "📅 هفتگی - 690,000",
                    callback_data="plan_weekly"
                )
            ],
            [
                InlineKeyboardButton(
                    "📅 ماهانه - 1,890,000",
                    callback_data="plan_monthly"
                )
            ]
        ]

        await update.message.reply_text(
            "💎 نوع اشتراک را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )



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

        if data and data[0]:

            status = "VIP"

            end = data[1]


        await update.message.reply_text(
            f"""👤 حساب کاربری

🆔 آیدی:
{user.id}

👤 نام:
{user.first_name}

💎 وضعیت:
{status}

📅 پایان اشتراک:
{end}"""
        )



    elif text == "☎️ پشتیبانی":

        await update.message.reply_text(
            "☎️ پشتیبانی\n\n@MazanhGoldAcademy"
        )



async def plan_select(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    plan = query.data.replace(
        "plan_",
        ""
    )

    save_plan(
        query.from_user.id,
        plan
    )


    await query.message.reply_text(
        f"""💎 پلن انتخاب شد

📅 نوع:
{PLANS[plan]["name"]}

💰 مبلغ:
{PLANS[plan]["price"]}

💳 شماره کارت:

6219 8619 0960 4646

👤 داود شکوری مقدم

📸 بعد از پرداخت عکس رسید را ارسال کنید."""
    )
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


    plan_text = "نامشخص"

    if result and result[0] in PLANS:

        plan_text = PLANS[result[0]]["name"]



    keyboard = [
        [
            InlineKeyboardButton(
                "✅ فعال کردن VIP",
                callback_data=f"vip_{user.id}"
            ),
            InlineKeyboardButton(
                "❌ رد کردن",
                callback_data=f"reject_{user.id}"
            )
        ]
    ]


    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo.file_id,
        caption=f"""📩 رسید جدید VIP

👤 نام:
{user.first_name}

🆔 آیدی:
{user.id}

📦 پلن انتخابی:
{plan_text}

🤖 یوزرنیم:
@{user.username if user.username else "ندارد"}""",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


    await update.message.reply_text(
        "✅ رسید ارسال شد. پس از بررسی مدیریت فعال می‌شود."
    )




async def vip_action(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data

    user_id = int(data.split("_")[1])


    if data.startswith("vip_"):


        activate_vip(user_id)


        await context.bot.send_message(
            chat_id=user_id,
            text=f"""🎉 اشتراک VIP شما فعال شد.

🔐 لینک ورود کانال VIP:

{VIP_LINK}

🥇 Gold Hunter | شکارچی مظنه طلا🏅"""
        )


        await query.edit_message_caption(
            "✅ VIP فعال شد."
        )


    elif data.startswith("reject_"):


        await context.bot.send_message(
            chat_id=user_id,
            text="❌ رسید شما تایید نشد."
        )


        await query.edit_message_caption(
            "❌ رسید رد شد."
        )





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
        pattern="check"
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



app.run_polling()