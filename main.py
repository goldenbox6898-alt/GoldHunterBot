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


SIGNAL_TYPE = {}
SIGNAL_TEXT = {}
SIGNAL_TARGET = {}

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

        days INTEGER,

        invited_by INTEGER DEFAULT 0,

        invites INTEGER DEFAULT 0

    )
    """)


    conn.commit()
    conn.close()



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
            INSERT INTO users
            (
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
                SET invites = invites + 1
                WHERE user_id=?
                """,
                (inviter,)
            )


    conn.commit()
    conn.close()



def save_plan(user_id, plan):

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE users
        SET plan=?, days=?
        WHERE user_id=?
        """,
        (
            plan,
            PLANS[plan]["days"],
            user_id
        )
    )


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


    days = result[0] if result and result[0] else 1


    end = datetime.now() + timedelta(days=days)


    cursor.execute(
        """
        UPDATE users
        SET vip=1,
        vip_end=?
        WHERE user_id=?
        """,
        (
            end.strftime("%Y-%m-%d"),
            user_id
        )
    )


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

        ["📢 مدیریت سیگنال"]

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


    inviter = None

    if context.args:

        try:

            inviter = int(context.args[0])

            if inviter == user.id:

                inviter = None

        except:

            inviter = None



    add_user(user, inviter)



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

به ربات رسمی شکارچی مظنه طلا خوش آمدید.

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



    #=========================
    # مدیریت سیگنال
    #=========================

    if text == "📢 مدیریت سیگنال":


        if user.id != ADMIN_ID:

            await update.message.reply_text(
                "⛔ شما دسترسی مدیریت ندارید."
            )

            return



        keyboard = [

            [
                InlineKeyboardButton(
                    "🟢 خرید",
                    callback_data="send_buy"
                )
            ],

            [
                InlineKeyboardButton(
                    "🔴 فروش",
                    callback_data="send_sell"
                )
            ]

        ]


        await update.message.reply_text(
            "نوع سیگنال را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


        return



    #=========================
    # سیگنال VIP
    #=========================


    if text == "📈 سیگنال VIP":


        conn = sqlite3.connect(DB)
        cursor = conn.cursor()


        cursor.execute(
            """
            SELECT vip,vip_end
            FROM users
            WHERE user_id=?
            """,
            (user.id,)
        )


        data = cursor.fetchone()

        conn.close()



        if data and data[0] == 1:


            await update.message.reply_text(

                f"""✅ اشتراک VIP فعال است.

📅 پایان:
{data[1]}

🔐 ورود به کانال VIP:""",

                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "ورود VIP",
                                url=VIP_LINK
                            )
                        ]
                    ]
                )

            )


        else:


            await update.message.reply_text(
                "⛔ اشتراک VIP ندارید."
            )



    #=========================
    # خرید اشتراک
    #=========================


    elif text == "💎 خرید اشتراک":


        keyboard = [

            [
                InlineKeyboardButton(
                    "روزانه 200 هزار",
                    callback_data="plan_daily"
                )
            ],

            [
                InlineKeyboardButton(
                    "هفتگی 690 هزار",
                    callback_data="plan_weekly"
                )
            ],

            [
                InlineKeyboardButton(
                    "ماهانه 1.890 میلیون",
                    callback_data="plan_monthly"
                )
            ]

        ]


        await update.message.reply_text(
            "💎 انتخاب پلن:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )



    #=========================
    # حساب کاربری
    #=========================


    elif text == "👤 حساب کاربری":


        conn = sqlite3.connect(DB)
        cursor = conn.cursor()


        cursor.execute(
            """
            SELECT vip,vip_end,invites
            FROM users
            WHERE user_id=?
            """,
            (user.id,)
        )


        data = cursor.fetchone()

        conn.close()


        await update.message.reply_text(

            f"""👤 حساب کاربری

🆔 آیدی:
{user.id}

👤 نام:
{user.first_name}

💎 وضعیت:
{"VIP" if data and data[0] else "عادی"}

📅 پایان:
{data[1] if data else "-"}

👥 دعوت موفق:
{data[2] if data else 0}
"""

        )



    #=========================
    # دعوت دوستان
    #=========================


    elif text == "👥 دعوت دوستان":


        link = f"https://t.me/GoldHunterMazanhSignalBot?start={user.id}"


        conn = sqlite3.connect(DB)
        cursor = conn.cursor()


        cursor.execute(
            "SELECT invites FROM users WHERE user_id=?",
            (user.id,)
        )


        result = cursor.fetchone()

        conn.close()


        count = result[0] if result else 0



        await update.message.reply_text(

            f"""🎁 سیستم دعوت دوستان

👥 تعداد دعوت:
{count}

🔗 لینک اختصاصی شما:

{link}

با دعوت دوستان هدیه دریافت کنید."""

        )



    elif text == "📚 آموزش‌ها":


        await update.message.reply_text(
            "📚 آموزش‌های اختصاصی Gold Hunter به زودی فعال می‌شود."
        )



    elif text == "☎️ پشتیبانی":


        await update.message.reply_text(
            "☎️ پشتیبانی:\n@MazanhGoldAcademy"
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
# دریافت نوع سیگنال
#=========================

async def signal_type(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        return


    if query.data == "send_buy":

        SIGNAL_TYPE[user_id] = "🟢 خرید"

    elif query.data == "send_sell":

        SIGNAL_TYPE[user_id] = "🔴 فروش"


    keyboard = [

    [
        InlineKeyboardButton(
            "📢 کانال عمومی",
            callback_data="target_public"
        )
    ],

    [
        InlineKeyboardButton(
            "💎 کانال VIP",
            callback_data="target_vip"
        )
    ],

    [
        InlineKeyboardButton(
            "🔥 هر دو کانال",
            callback_data="target_both"
        )
    ]

    ]

    await query.message.reply_text(
        f"""✅ نوع سیگنال انتخاب شد:

{SIGNAL_TYPE[user_id]}

حالا مقصد ارسال را انتخاب کنید:""",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
#=========================
# دریافت متن سیگنال
#=========================

async def receive_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if user.id != ADMIN_ID:
        return

    if user.id not in SIGNAL_TYPE:
        return


    SIGNAL_TEXT[user.id] = update.message.text


    keyboard = [

        [
            InlineKeyboardButton(
                "📢 ارسال عمومی",
                callback_data="send_public"
            )
        ],

        [
            InlineKeyboardButton(
                "🔐 ارسال VIP",
                callback_data="send_vip"
            )
        ],

        [
            InlineKeyboardButton(
                "🚀 ارسال هر دو",
                callback_data="send_both"
            )
        ]

    ]


    await update.message.reply_text(
        "✅ سیگنال دریافت شد.\n\n"
        "انتخاب کنید کجا ارسال شود:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
#=========================
# ارسال نهایی سیگنال
#=========================

async def send_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id


    if user_id != ADMIN_ID:
        return


    text = SIGNAL_TEXT.get(user_id)


    if not text:
        await query.message.reply_text(
            "❌ سیگنالی برای ارسال وجود ندارد."
        )
        return


    text = f"""
{text}

━━━━━━━━━━━━━━
🥇 Gold Hunter | شکارچی مظنه طلا🏅
👤 داود شکوری مقدم
"""


    if query.data == "send_public":

        await context.bot.send_message(
            chat_id=CHANNEL,
            text=text
        )


    elif query.data == "send_vip":

        await context.bot.send_message(
            chat_id=VIP_CHANNEL,
            text=text
        )


    elif query.data == "send_both":

        await context.bot.send_message(
            chat_id=CHANNEL,
            text=text
        )

        await context.bot.send_message(
            chat_id=VIP_CHANNEL,
            text=text
        )


    await query.message.reply_text(
        "✅ سیگنال با موفقیت ارسال شد."
    )


    SIGNAL_TEXT.pop(user_id, None)
    SIGNAL_TYPE.pop(user_id, None)
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
    CallbackQueryHandler(
        signal_type,
        pattern="^(send_buy|send_sell)$"
    )
)

app.add_handler(
    CallbackQueryHandler(
        send_signal,
        pattern="^(send_public|send_vip|send_both)$"
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        receive_signal
    ),
    group=1
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        buttons
    ),
    group=2
)


app.add_handler(
    MessageHandler(
        filters.PHOTO,
        receipt
    )
)

app.run_polling()