from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from datetime import datetime, timedelta
import json
import os

# DO NOT put the token here. Choreo will provide it via Environment Variables.
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

DATA_FILE = "/tmp/checking_data.json" # Using /tmp for temporary storage in Choreo

ASSIGNED_NAMES = [
    "Mao Peseth",
    "Chhinsy Pheav",
    "Chuon Chanthoeun",
    "Khorn Ehor"
]

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📅 Check Today", callback_data="check_today")],
        [InlineKeyboardButton("📊 Weekly Report", callback_data="weekly_report")]
    ]
    await update.message.reply_text(
        "🖥️ Computer Checking System\nChoose an option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "check_today":
        await show_name_selection(query)
    elif query.data.startswith("name_"):
        name = query.data.replace("name_", "")
        await submit_checkin(query, name)
    elif query.data == "weekly_report":
        await weekly_report(query)

async def show_name_selection(query):
    keyboard = [[InlineKeyboardButton(name, callback_data=f"name_{name}")] for name in ASSIGNED_NAMES]
    await query.message.reply_text("👤 Select your name:", reply_markup=InlineKeyboardMarkup(keyboard))

async def submit_checkin(query, name):
    today = datetime.now().strftime("%Y-%m-%d")
    data = load_data()
    if today not in data:
        data[today] = []
    if name in data[today]:
        await query.message.reply_text(f"⚠️ Already checked today:\n📅 {today}\n👤 {name}")
        return
    data[today].append(name)
    save_data(data)
    display_date = datetime.now().strftime("%d/%m/%Y")
    await query.message.reply_text(f"✅ Checking Successful\n📅 Checking date: {display_date}\n👤 By: {name}")

async def weekly_report(query):
    data = load_data()
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)
    report = "📊 Weekly Computer Checking Report\n"
    report += f"📅 {monday.strftime('%d/%m')} - {friday.strftime('%d/%m')}\n\n"
    missing_days = []
    for i in range(5):
        day = monday + timedelta(days=i)
        day_key = day.strftime("%Y-%m-%d")
        day_name = day.strftime("%A")
        if day_key in data:
            report += f"✅ {day_name}: Checked\n"
        else:
            report += f"❌ {day_name}: Missing\n"
            missing_days.append(day_name)
    if missing_days:
        report += "\n⚠️ Missing Days:\n" + ", ".join(missing_days)
    await query.message.reply_text(report)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables.")
    else:
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        print("Bot is running...")
        app.run_polling()