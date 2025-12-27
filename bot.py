import os
import random
import json
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- 1. ВЕБ-СЕРВЕР (щоб Render не "засинав") ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Kapyland працює!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. ЛОГІКА БОТА ---
DB_FILE = "kapyland_db.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_name = update.effective_user.first_name
    
    if user_id not in kapyland_db:
        kapyland_db[user_id] = {"weight": 20.0, "name": user_name}
        save_data(kapyland_db)
        await update.message.reply_text(f"✨ Вітаємо у Kapyland, {user_name}! Твоя капібара важить 20кг. Годуй її командою /feed!")
    else:
        await update.message.reply_text("У тебе вже є капібара! Перевір вагу: /stats або лідерів: /top.")

async def feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in kapyland_db:
        gain = round(random.uniform(0.5, 2.5), 2)
        kapyland_db[user_id]["weight"] = round(kapyland_db[user_id]["weight"] + gain, 2)
        save_data(kapyland_db)
        await update.message.reply_text(f"🍎 Смакота! +{gain}кг. Тепер вага: {kapyland_db[user_id]['weight']}кг")
    else:
        await update.message.reply_text("Спочатку напиши /start!")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not kapyland_db:
        await update.message.reply_text("У Kapyland поки порожньо...")
        return

    # Сортування за вагою (від найбільшої)
    sorted_users = sorted(kapyland_db.items(), key=lambda x: x[1]['weight'], reverse=True)
    
    msg = "🏆 **ТОП КАПІБАР KAPYLAND** 🏆\n\n"
    for i, (uid, info) in enumerate(sorted_users[:10]): # Топ 10
        name = info.get("name", "Анонім")
        weight = info.get("weight", 0)
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🐾"
        msg += f"{medal} {name}: {weight}кг\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in kapyland_db:
        weight = kapyland_db[user_id]["weight"]
        await update.message.reply_text(f"📊 Твоя капібара важить **{weight}кг**.")
    else:
        await update.message.reply_text("У тебе ще немає капібари. Напиши /start.")

async def delete_kapy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in kapyland_db:
        del kapyland_db[user_id]
        save_data(kapyland_db)
        await update.message.reply_text("❌ Твоя капібара пішла у ліс. Тепер ти можеш почати заново через /start.")
    else:
        await update.message.reply_text("У тебе немає капібари для видалення.")

def main():
    threading.Thread(target=run_flask, daemon=True).start()

    TOKEN = os.environ.get("BOT_TOKEN")
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("feed", feed))
    application.add_handler(CommandHandler("top", leaderboard))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("delete", delete_kapy))
    
    application.run_polling()

if __name__ == "__main__":
    kapyland_db = load_data()
    main()