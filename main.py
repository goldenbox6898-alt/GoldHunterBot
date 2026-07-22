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



# =========================
# حافظه موقت سیگنال
# =========================


SIGNAL_TYPE = {}

SIGNAL_TEXT = {}



# =========================
# پلن‌ها
# =========================


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
# =========================
# دیتابیس
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



# =========================
# ذخیره پلن خرید
# =========================


def save_plan(user_id, plan):

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE users

        SET plan=?,
            days=?

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




# =========================
# فعال کردن VIP
# =========================


def activate_vip(user_id):

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()



    cursor.execute(
        """
        SELECT days

        FROM users

        WHERE user_id=?
        """,

        (user_id,)
    )


    result = cursor.fetchone()



    days = 1


    if result and result[0]:

        days = result[0]



    end_date = datetime.now() + timedelta(days=days)



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
# =========================
# منوی اصلی
# =========================


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



# =========================
# استارت ربات
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

            "❌ برای استفاده از ربات ابتدا در کانال رسمی عضو شوید.",

            reply_markup=InlineKeyboardMarkup(keyboard)

        )


        return






    await update.message.reply_text(


        f"""🥇 Gold Hunter | شکارچی مظنه طلا 🏅


سلام {user.first_name} 🌹


✅ عضویت شما تایید شد.


به ربات رسمی شکارچی مظنه طلا خوش آمدید.


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


📅 تاریخ پایان:

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

                "⛔ اشتراک VIP شما فعال نیست."

            )





    # =========================
    # خرید اشتراک
    # =========================


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

            "💎 انتخاب نوع اشتراک:",

            reply_markup=InlineKeyboardMarkup(keyboard)

        )





    # =========================
    # حساب کاربری
    # =========================


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


📅 پایان اشتراک:

{data[1] if data else "-"}


👥 دعوت موفق:

{data[2] if data else 0}

"""

        )




    # =========================   
    # دعوت دوستان
    # =========================

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

🔗 لینک اختصاصی کانال:
{link}

🌊 ثبت نام دریا گلد:
{DARYA_LINK}

🎁 کد معرف:
{REF_CODE}

با دعوت دوستان هدیه دریافت کنید."""
    )








    # =========================
    # آموزش‌ها
    # =========================


    elif text == "📚 آموزش‌ها":


        await update.message.reply_text(

            "📚 آموزش‌های اختصاصی Gold Hunter به زودی فعال می‌شود."

        )





    # =========================
    # پشتیبانی
    # =========================


    elif text == "☎️ پشتیبانی":


        await update.message.reply_text(

            "☎️ پشتیبانی:\n@MazanhGoldAcademy"

        )
# =========================
# انتخاب پلن
# =========================


async def plan_select(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query


    await query.answer()


    user = query.from_user



    add_user(user)



    plan = query.data.replace("plan_", "")



    save_plan(

        user.id,

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



📸 بعد از پرداخت، عکس رسید را برای ربات ارسال کنید."""

    )





# =========================
# دریافت رسید پرداخت
# =========================


async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):


    user = update.effective_user


    photo = update.message.photo[-1]



    conn = sqlite3.connect(DB)

    cursor = conn.cursor()



    cursor.execute(

        """

        SELECT plan

        FROM users

        WHERE user_id=?

        """,

        (user.id,)

    )


    result = cursor.fetchone()


    conn.close()





    plan_name = "نامشخص"



    if result:


        if result[0] == "daily":

            plan_name = "روزانه"



        elif result[0] == "weekly":

            plan_name = "هفتگی"



        elif result[0] == "monthly":

            plan_name = "ماهانه"






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


        caption=f"""📩 رسید جدید پرداخت



👤 نام:

{user.first_name}



🆔 آیدی:

{user.id}



🤖 یوزرنیم:

@{user.username if user.username else "ندارد"}



📦 پلن:

{plan_name}

""",


        reply_markup=InlineKeyboardMarkup(keyboard)

    )






    await update.message.reply_text(


        "✅ رسید شما ارسال شد.\n\nپس از تایید مدیریت، اشتراک فعال می‌شود."

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



        activate_vip(user_id)



        await context.bot.send_message(


            chat_id=user_id,


            text=f"""🎉 پرداخت شما تایید شد.



✅ اشتراک VIP فعال گردید.



🔐 لینک ورود به کانال VIP:



{VIP_LINK}

"""

        )



        await query.edit_message_caption(

            caption="✅ پرداخت تایید شد و VIP فعال گردید."

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
# انتخاب نوع سیگنال
# =========================


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



حالا متن سیگنال را ارسال کنید:"""

    )
# =========================
# دریافت متن سیگنال
# =========================


async def receive_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if update.message.text == "📢 مدیریت سیگنال":
        return

    if user.id != ADMIN_ID:
        return

    if user.id not in SIGNAL_TYPE:
        return

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

                "💎 ارسال VIP",

                callback_data="send_vip"

            )

        ],


        [

            InlineKeyboardButton(

                "🔥 ارسال هر دو",

                callback_data="send_both"

            )

        ]

    ]





    await update.message.reply_text(


        "✅ سیگنال دریافت شد.\n\nمحل ارسال را انتخاب کنید:",


        reply_markup=InlineKeyboardMarkup(keyboard)

    )







# =========================
# ارسال نهایی سیگنال
# =========================


async def send_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):


    query = update.callback_query


    await query.answer()



    user_id = query.from_user.id



    if user_id != ADMIN_ID:

        return





    text = SIGNAL_TEXT.get(user_id)



    if not text:



        await query.message.reply_text(

            "❌ متن سیگنال پیدا نشد."

        )

        return






    final_text = f"""

{text}



━━━━━━━━━━━━━━

🥇 Gold Hunter | شکارچی مظنه طلا 🏅

👤 داود شکوری مقدم

"""






    if query.data == "send_public":


        await context.bot.send_message(

            chat_id=CHANNEL,

            text=final_text

        )




    elif query.data == "send_vip":


        await context.bot.send_message(

            chat_id=VIP_CHANNEL,

            text=final_text

        )




    elif query.data == "send_both":


        await context.bot.send_message(

            chat_id=CHANNEL,

            text=final_text

        )



        await context.bot.send_message(

            chat_id=VIP_CHANNEL,

            text=final_text

        )







    await query.message.reply_text(

        "✅ سیگنال ارسال شد."

    )




    SIGNAL_TEXT.pop(user_id, None)

    SIGNAL_TYPE.pop(user_id, None)
# =========================
# اجرای ربات
# =========================


init_db()



app = Application.builder().token(TOKEN).build()





# =========================
# دستورات
# =========================



app.add_handler(

    CommandHandler(

        "start",

        start

    )

)





# =========================
# بررسی عضویت
# =========================


app.add_handler(

    CallbackQueryHandler(

        check,

        pattern="^check$"

    )

)





# =========================
# انتخاب پلن
# =========================


app.add_handler(

    CallbackQueryHandler(

        plan_select,

        pattern="^plan_"

    )

)





# =========================
# تایید پرداخت
# =========================


app.add_handler(

    CallbackQueryHandler(

        vip_action,

        pattern="^(vip_|reject_)"

    )

)





# =========================
# انتخاب نوع سیگنال
# =========================


app.add_handler(

    CallbackQueryHandler(

        signal_type,

        pattern="^(send_buy|send_sell)$"

    )

)





# =========================
# ارسال سیگنال
# =========================


app.add_handler(

    CallbackQueryHandler(

        send_signal,

        pattern="^(send_public|send_vip|send_both)$"

    )

)





# =========================
# پیام‌های متنی منو
# =========================


app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        buttons
    ),
    group=0
)





# =========================
# متن سیگنال ادمین
# =========================


app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        receive_signal
    ),
    group=1
)





# =========================
# رسید پرداخت عکس
# =========================


app.add_handler(

    MessageHandler(

        filters.PHOTO,

        receipt

    )

)





print("🤖 Gold Hunter Bot Started")



app.run_polling()