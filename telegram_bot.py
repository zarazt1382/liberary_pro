import json
import os
import requests
import jdatetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

CONFIG_FILE = "telegram_config.json"
USERS_FILE = "telegram_users.json"


# ---------------- Config ----------------
def load_config():
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError("telegram_config.json not found")

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


config = load_config()
BOT_TOKEN = config["bot_token"]


# ---------------- Users ----------------
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


telegram_users = load_users()


# ---------------- Utils ----------------
def calculate_days_difference(return_date_str):
    """
    return_date_str: YYYY-MM-DD (شمسی)
    """
    y, m, d = map(int, return_date_str.split("-"))
    return_date = jdatetime.date(y, m, d)
    today = jdatetime.date.today()
    return (return_date - today).days


def build_message(borrower_name, book_title, days_diff):
    if days_diff > 0:
        return (
            f"📚 یادآوری کتابخانه\n\n"
            f"👤 {borrower_name}\n"
            f"📖 {book_title}\n"
            f"⏳ {days_diff} روز تا تاریخ بازگشت باقی مانده است."
        )
    elif days_diff == 0:
        return (
            f"📚 یادآوری کتابخانه\n\n"
            f"👤 {borrower_name}\n"
            f"📖 {book_title}\n"
            f"⚠️ امروز آخرین مهلت بازگشت کتاب است."
        )
    else:
        return (
            f"⛔ اخطار تأخیر در بازگشت کتاب\n\n"
            f"👤 {borrower_name}\n"
            f"📖 {book_title}\n"
            f"❗ {-days_diff} روز از موعد بازگشت گذشته است."
        )


# ---------------- Telegram Handlers ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 سلام!\n\n"
        "لطفاً شماره دانشجویی خود را ارسال کنید "
        "تا یادآوری‌های کتابخانه فعال شود."
    )


async def register_student_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    student_id = update.message.text.strip()
    chat_id = update.message.chat_id

    telegram_users[student_id] = {
        "chat_id": chat_id,
        "first_name": update.message.from_user.first_name,
        "username": update.message.from_user.username
    }
    save_users(telegram_users)

    import os
    import json 

    users_file = "library_users_fa.json"
    updated = False
    if os.path.exists(users_file):
        with open(users_file, "r", encoding="utf-8") as f:
            users = json.load(f)
        for user in users:
            if user.get('student_id') == student_id:
                user['telegram_chat_id'] = f'{chat_id}'
                updated = True
                break
        if updated:
            with open(users_file, "w", encoding="utf-8") as f:
                json.dump(users, f, ensure_ascii=False, indent=4)
            print(f"✅ Updated telegram_chat_id for student {student_id} in library_users_fa.json")  # برای دیباگ در کنسول
        else:
            print(f"⚠️ Student {student_id} not found in library_users_fa.json")  # اگر کاربر در لیست GUI نبود

    await update.message.reply_text(
        "✅ ثبت انجام شد!\n"
        "از این پس پیام‌های یادآوری کتابخانه برای شما ارسال می‌شود."
    )

# ---------------- Send Reminder (Called from GUI) ----------------
def send_loan_reminder(chat_id, borrower_name, book_title, borrow_date, return_date):
    days_diff = calculate_days_difference(return_date)
    message = build_message(borrower_name, book_title, days_diff)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    response = requests.post(url, json=payload)
    return response.status_code == 200

# ---------------- Bot Runner ----------------
def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, register_student_id)
    )

    print("🤖 Telegram bot is running...")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
