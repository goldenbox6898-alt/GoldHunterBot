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
        plan TEXT DEFAULT 'daily',
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

        # اضافه شدن دعوت موفق
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
# =========================
# منوی اصلی
# =========================

def main_menu():

    keyboard = [
        ["📈 سیگنال VIP", "💎 خرید اشتراک"],
        ["👤 حساب کاربری", "👥 دعوت دوستان"],
        ["🎁 هدیه دعوت", "📚 آموزش‌ها"],
        ["☎️ پشتیبانی", "📢 مدیریت سیگنال"],
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
            "❌ برای استفاده از ربات ابتدا عضو کانال شوید.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return


    await update.message.reply_text(

        f"""🥇 Gold Hunter | شکارچی مظنه طلا 🏅

سلام {user.first_name} 🌹

✅ عضویت شما تایید شد.

یکی از گزینه‌های زیر را انتخاب کنید.""",

        reply_markup=main_menu()
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

            keyboard = [[
                InlineKeyboardButton(
                    "💎 ورود به کانال VIP",
                    url=VIP_LINK
                )
            ]]


            await update.message.reply_text(
                f"""✅ اشتراک شما فعال است.

📅 پایان اشتراک:
{data[1]}""",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )


        else:

            await update.message.reply_text(
                "⛔ اشتراک VIP شما فعال نیست.\n\nاز بخش 💎 خرید اشتراک اقدام کنید."
            )


    # =========================
    # خرید اشتراک
    # =========================

    elif text == "💎 خرید اشتراک":

        keyboard = [

            [
                InlineKeyboardButton(
                    "📅 روزانه | 200 هزار تومان",
                    callback_data="plan_daily"
                )
            ],

            [
                InlineKeyboardButton(
                    "📅 هفتگی | 690 هزار تومان",
                    callback_data="plan_weekly"
                )
            ],

            [
                InlineKeyboardButton(
                    "📅 ماهانه | 1,890,000 تومان",
                    callback_data="plan_monthly"
                )
            ]

        ]


        await update.message.reply_text(
            "💎 نوع اشتراک را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # =========================
    # حساب کاربری
    # =========================

    elif text == "👤 حساب کاربری":

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT vip,vip_end,invites FROM users WHERE user_id=?",
            (user.id,)
        )

        data = cursor.fetchone()

        conn.close()


        vip = "عادی"
        end = "-"
        invites = 0


        if data:

            if data[0] == 1:
                vip = "VIP"

            end = data[1] if data[1] else "-"
            invites = data[2]


        await update.message.reply_text(
            f"""👤 حساب کاربری

🆔 آیدی:
{user.id}

👤 نام:
{user.first_name}

🤖 یوزرنیم:
@{user.username if user.username else "ندارد"}

💎 وضعیت اشتراک:
{vip}

📅 پایان اشتراک:
{end}

👥 دعوت موفق:
{invites}"""
        )


    # =========================
    # دعوت دوستان
    # =========================

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
            # هدیه دعوت
    elif text == "🎁 هدیه دعوت":

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT invites FROM users WHERE user_id=?",
            (user.id,)
        )

        result = cursor.fetchone()

        conn.close()

        invites = result[0] if result else 0


        if invites >= 30:
            gift = "🎉 هدیه شما: ۳۰ روز اشتراک VIP"

        elif invites >= 15:
            gift = "🎉 هدیه شما: ۷ روز اشتراک VIP"

        elif invites >= 5:
            gift = "🎉 هدیه شما: ۱ روز اشتراک VIP"

        else:
            gift = "❌ هنوز به حد نصاب نرسیده‌اید."


        await update.message.reply_text(
            f"""🎁 هدیه دعوت

👥 دعوت موفق:
{invites}

{gift}

━━━━━━━━━━━━━━

🏆 قوانین هدیه:

✅ ۵ دعوت = ۱ روز VIP
✅ ۱۵ دعوت = ۷ روز VIP
✅ ۳۰ دعوت = ۳۰ روز VIP"""
        )


    # =========================
    # آموزش‌ها
    # =========================

    elif text == "📚 آموزش‌ها":

        await update.message.reply_text(
            "📚 بخش آموزش‌ها به‌زودی فعال می‌شود."
        )


    # =========================
    # پشتیبانی
    # =========================

    elif text == "☎️ پشتیبانی":

        await update.message.reply_text(
            "☎️ پشتیبانی:\n\n@MazanhGoldAcademy"
        )


    # =========================
    # مدیریت سیگنال
    # =========================

    elif text == "📢 مدیریت سیگنال":

        await signal_menu(update, context)
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


    user_id = query.from_user.id


    # ذخیره پلن انتخابی کاربر

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET plan=?
        WHERE user_id=?
        """,
        (
            plan,
            user_id
        )
    )

    conn.commit()
    conn.close()



    await query.message.reply_text(

        f"""💎 پلن انتخابی شما:

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
            )

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
        "✅ رسید پرداخت شما ارسال شد.\n\nپس از تایید مدیریت، اشتراک فعال می‌شود."
    )
# =========================
# تایید یا رد پرداخت
# =========================

async def vip_action(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data

    user_id = int(data.split("_")[1])


    # =========================
    # تایید پرداخت
    # =========================

    if data.startswith("vip_"):


        conn = sqlite3.connect(DB)
        cursor = conn.cursor()


        cursor.execute(
            "SELECT plan FROM users WHERE user_id=?",
            (user_id,)
        )


        result = cursor.fetchone()


        plan = result[0] if result else "daily"



        days = {

            "daily": 1,

            "weekly": 7,

            "monthly": 30

        }



        vip_days = days.get(plan, 1)



        end_date = datetime.now() + timedelta(days=vip_days)



        cursor.execute(

            """
            UPDATE users

            SET vip=1,
                vip_end=?

            WHERE user_id=?
            """,

            (
                end_date.strftime("%Y-%m-%d"),
                user_id
            )

        )


        conn.commit()
        conn.close()



        await context.bot.send_message(

            chat_id=user_id,

            text=f"""🎉 پرداخت شما تایید شد.

✅ اشتراک VIP فعال شد.

📦 پلن:
{plan}

📅 پایان اشتراک:
{end_date.strftime("%Y-%m-%d")}

🔐 لینک کانال VIP:

{VIP_LINK}"""

        )



        await query.edit_message_caption(
            caption="✅ پرداخت تایید شد."
        )



    # =========================
    # رد پرداخت
    # =========================

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
        await update.message.reply_text(
            "⛔ دسترسی ندارید."
        )
        return


    keyboard = [

        [
            InlineKeyboardButton(
                "🟢 سیگنال خرید",
                callback_data="send_buy"
            )
        ],

        [
            InlineKeyboardButton(
                "🔴 سیگنال فروش",
                callback_data="send_sell"
            )
        ]

    ]


    await update.message.reply_text(
        "📢 نوع سیگنال را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
# =========================
# انتخاب نوع سیگنال
# =========================

async def signal_type_select(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()


    user_id = query.from_user.id


    if user_id != ADMIN_ID:
        return


    if query.data == "send_buy":

        SIGNAL_TYPE[user_id] = "🟢 خرید"


    elif query.data == "send_sell":

        SIGNAL_TYPE[user_id] = "🔴 فروش"


    await query.message.reply_text(
        "📝 متن سیگنال را ارسال کنید:"
    )
# =========================
# ارسال سیگنال
# =========================

async def send_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user


    if user.id != ADMIN_ID:
        return


    if user.id not in SIGNAL_TYPE:
        return


    signal_type = SIGNAL_TYPE[user.id]

    text = update.message.text


    signal = f"""🥇 Gold Hunter | شکارچی مظنه طلا 🏅


{signal_type} سیگنال جدید


━━━━━━━━━━━━━━

{text}

━━━━━━━━━━━━━━

⚡ مدیریت سرمایه را رعایت کنید.

@GoldHunter68980
"""


    await context.bot.send_message(

        chat_id=VIP_CHANNEL,

        text=signal

    )


    await update.message.reply_text(
        "✅ سیگنال با موفقیت در کانال VIP ارسال شد."
    )


    del SIGNAL_TYPE[user.id]
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


# دریافت رسید پرداخت
app.add_handler(
    MessageHandler(
        filters.PHOTO,
        receipt
    )
)
# انتخاب نوع سیگنال
app.add_handler(
    CallbackQueryHandler(
        signal_type_select,
        pattern="^(send_buy|send_sell)$"
    )
)


# ارسال متن سیگنال توسط ادمین
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        send_signal
    ),
    group=1
)
print("🤖 Gold Hunter Bot Started")

init_db()

app.run_polling()