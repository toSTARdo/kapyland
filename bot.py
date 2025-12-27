import os
import random
import json
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- 1. THE WEB SERVER (To keep Render awake) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Kapyland is Online!"

def run_flask():
    # Render provides a PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. THE BOT LOGIC ---
DB_FILE = "kapyland_db.json"
kapyland_db = {}

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data():
    with open(DB_FILE, 'w') as f:
        json.dump(kapyland_db, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in kapyland_db:
        kapyland_db[user_id] = {"weight": 20.0}
        save_data()
        await update.message.reply_text("✨ Welcome to Kapyland! Your Capybara weighs 20kg. Use /feed!")
    else:
        await update.message.reply_text("You already have a Capybara!")

async def feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in kapyland_db:
        gain = round(random.uniform(0.5, 2.0), 2)
        kapyland_db[user_id]["weight"] += gain
        save_data()
        await update.message.reply_text(f"🍎 Fed! It gained {gain}kg. Total: {kapyland_db[user_id]['weight']}kg")

def main():
    # Start Flask in a separate thread
    threading.Thread(target=run_flask, daemon=True).start()

    # Start Telegram Bot
    TOKEN = os.environ.get("BOT_TOKEN") # We will set this in Render dashboard
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("feed", feed))
    
    application.run_polling()

if __name__ == "__main__":
    kapyland_db = load_data()
    main()