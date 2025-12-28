import os
import random
import threading
from datetime import datetime
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import pymongo

# --- 1. WEB SERVER (For Render Health Checks) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "🐾 Kapyland is running with MongoDB Atlas!"

def run_flask():
    # Render uses port 8080 by default, or provides a PORT env var
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. DATABASE SETUP ---
# You must set MONGO_URI in Render Environment Variables
MONGO_URI = os.environ.get("MONGO_URI")
client = pymongo.MongoClient(MONGO_URI)
db = client["kapyland_db"]
users_col = db["users"]

# --- 3. DATA & TEXTS ---

ORIGIN_STORIES = [
    "📦 Ти знайшов заклеєну коробку біля смітника. Всередині була вона — 20 кілограмів чистої апатії.",
    "🃏 Ти виграв цю капібару в карти у привокзального безхатька. Він виглядав щасливим, коли йшов геть...",
    "🌑 Вона просто з'явилася у твоїй кімнаті посеред ночі. Ти не знаєш як, але тепер ти мусиш її годувати.",
    "🏢 Ти купив її через оголошення в даркнеті в розділі 'Помилки природи'. Доставка була безкоштовною.",
    "🎒 Ти йшов лісом і побачив, як капібара намагається вкрасти чийсь рюкзак. Тепер вона твоя проблема.",
    "🛸 Яскраве світло, звук працюючого пилосмока, і ось вона — висаджена інопланетянами прямо тобі під двері.",
    "💳 Ти випадково натиснув 'Купити зараз' на сумнівному сайті під час безсоння. Тепер у тебе мінус на карті і плюс капібара.",
    "🕵️ Тобі передали її люди в чорних плащах, прошепотівши: 'Бережи її, вона знає забагато'."
]

EDGY_JOKES = [
    "Ще один шматок, і вона вибухне, забравши з собою цей чат і твоє майбутнє 🧨",
    "Ще один шматочок, і вона пригравітує Місяць до Землі 🌌",
    "Твоя капібара виглядає так, ніби вона щойно з'їла чиїсь надії та мрії 💭",
    "Твоя капібара стала на крок ближче до ідеальної форми кулі ⚪",
    "Вона їсть, щоб забути про порожнечу ventilated всередині. Як і ти... 🕳️",
    "Сподіваюся, ти теж так дбаєш про власне здоров'я, як про цю товстуню... 🧂",
    "Вона стає настільки великою, що скоро держава забере її на прогодівлю ЗСУ 🫡",
    "Це не вага, це накопичена ненависть до людства 😈",
    "Твоя капібара бачила пекло, і сказала, що там недостатньо апельсинів 🍊",
    "Вона занадто розслаблена для того, хто перебуває в одному кроці від проблем із серцем 💧" 
]

FAIL_MESSAGES = [
    "Її знудило твоїми АТБшними апельсинами та отримала в бонус діарею 🤢",
    "Вона впала в екзистенційну кризу від останніх новин і відмовилася їсти 📺",
    "Капібарка вирішила продати частину душі. Хто ж знав що вона теж має вагу? ⚖️",
    "Твоя капібара влаштувала бойкот через твою поведінку останнім часом 🪧",
    "У неї випали зуби від твого розбещеного раціону. Тепер вона харчується тільки енергією сонця і чаю 🍵"
]

EQUILIBRIUM_MESSAGES = [
    "Капібара на відміну від тебе пішла мацати траву 🌱",
    "Сила волі мандаринки виявилася сильніша і вона не перетравилася 🍊",
    "Вона проігнорувала твої намагання. Вона вища за це 🏔️",
    "Капібарка змерзла і вийшла в нуль, спаливши калорії ❄️"
]

FEED_RESTRICTION_JOKES = [
    "🚫 Гроші закінчилися, апельсини в кредит більше не дають",
    "🚫 Ветеринар заборонив її годувати сьогодні, бо діагностував ожиріння, діабет та критичне мислення",
    "🚫 Капібара оголосила ситу сієсту. Приходь завтра",
    "🚫 Твоя кредитка заблокована через підозрілу активність у відділі фруктів",
    "🚫 Твоя капібара стала більша за синього кита і була забрана морськими біологами. Повернуть завтра"
]

# --- ДОПОМІЖНА ЛОГІКА ДЛЯ ЛОКАЛЬНОГО ТОПУ ---

def update_chat_list(user_id, chat_id, full_name):
    """Оновлює список чатів, де 'засвітився' користувач"""
    users_col.update_one(
        {"_id": user_id},
        {
            "$addToSet": {"chats": chat_id},
            "$set": {"full_name": full_name}
        },
        upsert=True
    )

# --- 4. BOT COMMANDS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    chat_id = str(update.effective_chat.id)
    full_name = update.effective_user.full_name
    
    user_data = users_col.find_one({"_id": user_id})
    
    if not user_data:
        new_user = {
            "_id": user_id,
            "weight": 20.0, 
            "kapy_name": "Безіменна булочка",
            "last_feed_date": "",
            "chats": [chat_id],
            "full_name": full_name
        }
        users_col.insert_one(new_user)
        
        story = random.choice(ORIGIN_STORIES)
        await update.message.reply_text(
            f"✨ **Вітаємо у Kapyland!** ✨\n\n"
            f"{story}\n\n"
            f"🍊 Зараз вона важить **20кг**.\n"
            f"🏷️ Дай їй ім'я: `/name Кличка`.\n"
            f"🥗 Годуй через /feed!", 
            parse_mode="Markdown"
        )
    else:
        update_chat_list(user_id, chat_id, full_name)
        await update.message.reply_text("🐾 Твоя капібара все ще тут. Перевір /stats.")

async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    chat_id = str(update.effective_chat.id)
    new_name = " ".join(context.args)
    if not new_name:
        await update.message.reply_text("📝 Пиши: `/name Ім'я`", parse_mode="Markdown")
        return
    
    update_chat_list(user_id, chat_id, update.effective_user.full_name)
    result = users_col.update_one({"_id": user_id}, {"$set": {"kapy_name": new_name}})
    if result.matched_count > 0:
        await update.message.reply_text(f"✅ Тепер цю купу хутра звати **{new_name}**.")
    else:
        await update.message.reply_text("❌ Спочатку /start!")

async def feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    chat_id = str(update.effective_chat.id)
    user_data = users_col.find_one({"_id": user_id})

    if not user_data:
        await update.message.reply_text("⚠️ Напиши /start, довбню.")
        return

    update_chat_list(user_id, chat_id, update.effective_user.full_name)
    today = datetime.now().strftime("%Y-%m-%d")
    if user_data.get("last_feed_date") == today:
        await update.message.reply_text(random.choice(FEED_RESTRICTION_JOKES))
        return

    rand_val = random.random()
    current_weight = user_data["weight"]
    k_name = user_data["kapy_name"]

    if rand_val < 0.45:
        loss = round(random.uniform(2.0, 5.0), 2)
        new_weight = max(1.0, round(current_weight - loss, 2))
        msg = f"📉 **{k_name}** схудла на {loss}кг!\n_{random.choice(FAIL_MESSAGES)}_"
    elif rand_val < 0.55:
        new_weight = current_weight
        msg = f"⚖️ **{k_name}** не змінила вагу.\n_{random.choice(EQUILIBRIUM_MESSAGES)}_"
    else:
        gain = round(random.uniform(0.5, 3.5), 2)
        new_weight = round(current_weight + gain, 2)
        msg = (f"🍊 **{k_name}** поїла! +{gain}кг.\n"
               f"⚖️ Вага: **{new_weight}кг**.\n\n"
               f"_{random.choice(EDGY_JOKES)} _")
            
    users_col.update_one(
        {"_id": user_id}, 
        {"$set": {"weight": new_weight, "last_feed_date": today}}
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    
    # Фільтруємо ТОП: тільки ті, хто в цьому чаті
    top_users = users_col.find({"chats": chat_id}).sort("weight", -1).limit(10)
    
    msg = "🏆 **ЗАЛА СЛАВИ ТА ОЖИРІННЯ ЧАТУ** 🏆\n\n"
    count = 0
    for i, user in enumerate(top_users):
        count += 1
        name = user.get("kapy_name", "Щось жирне")
        owner = user.get("full_name", "Анонім")
        weight = user.get("weight", 0)
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🐾"
        msg += f"{medal} {name} ({owner}): **{weight}кг**\n"
    
    if count == 0:
        await update.message.reply_text("💨 У цьому чаті поки ніхто не годував капібару.")
    else:
        await update.message.reply_text(msg, parse_mode="Markdown")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = users_col.find_one({"_id": user_id})
    if user_data:
        await update.message.reply_text(f"📊 Капібара **{user_data['kapy_name']}** важить **{user_data['weight']}кг**. 🌿")
    else:
        await update.message.reply_text("💨 У тебе немає капібари.")

async def delete_kapy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    result = users_col.delete_one({"_id": user_id})
    if result.deleted_count > 0:
        await update.message.reply_text("🌊 Твоя капібара пішла навіки купатися в теплі джерела. Тепер ти зовсім один. 🧘‍♂️")
    else:
        await update.message.reply_text("❔ Тут нема чого видаляти.")

# --- 5. MAIN EXECUTION ---

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN not found!")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("name", set_name))
    application.add_handler(CommandHandler("feed", feed))
    application.add_handler(CommandHandler("top", leaderboard))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("delete", delete_kapy))

    print("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()