import os
import random
import json
import threading
from datetime import datetime
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- 1. ВЕБ-СЕРВЕР ---
app = Flask(__name__)

@app.route('/')
def home():
    return "🐾 Kapyland працює!"

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

# --- СПИСКИ ЖАРТІВ ---

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
    "Вона їсть, щоб забути про порожнечу всередині. Як і ти... 🕳️",
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in kapyland_db:
        kapyland_db[user_id] = {
            "weight": 20.0, 
            "kapy_name": "Безіменна булочка",
            "last_feed_date": "" 
        }
        save_data(kapyland_db)
        
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
        await update.message.reply_text("🐾 Твоя капібара все ще тут. Перевір /stats.")

async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in kapyland_db:
        await update.message.reply_text("❌ Спочатку /start!")
        return
    new_name = " ".join(context.args)
    if not new_name:
        await update.message.reply_text("📝 Пиши: `/name Ім'я`", parse_mode="Markdown")
        return
    kapyland_db[user_id]["kapy_name"] = new_name
    save_data(kapyland_db)
    await update.message.reply_text(f"✅ Тепер цю купу хутра звати **{new_name}**.")

async def feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in kapyland_db:
        today = datetime.now().strftime("%Y-%m-%d")
        last_fed = kapyland_db[user_id].get("last_feed_date", "")

        if last_fed == today:
            restriction_msg = random.choice(FEED_RESTRICTION_JOKES)
            await update.message.reply_text(f"{restriction_msg}")
            return

        rand_val = random.random()
        k_name = kapyland_db[user_id].get("kapy_name", "Капібара")

        if rand_val < 0.45:
            loss = round(random.uniform(2.0, 5.0), 2)
            kapyland_db[user_id]["weight"] = max(1.0, round(kapyland_db[user_id]["weight"] - loss, 2))
            joke = random.choice(FAIL_MESSAGES)
            msg = f"📉 **{k_name}** схудла на {loss}кг!\n_{joke}_"
        
        elif rand_val < 0.55:
            joke = random.choice(EQUILIBRIUM_MESSAGES)
            msg = f"⚖️ **{k_name}** не змінила вагу.\n_{joke}_"
        
        else:
            gain = round(random.uniform(0.5, 3.5), 2)
            kapyland_db[user_id]["weight"] = round(kapyland_db[user_id]["weight"] + gain, 2)
            joke = random.choice(EDGY_JOKES)
            msg = (f"🍊 **{k_name}** поїла! +{gain}кг.\n"
                   f"⚖️ Вага: **{kapyland_db[user_id]['weight']}кг**.\n\n"
                   f"_{joke}_")
            
        kapyland_db[user_id]["last_feed_date"] = today
        save_data(kapyland_db)
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ Напиши /start, довбню.")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not kapyland_db:
        await update.message.reply_text("💨 Тут пусто.")
        return
    sorted_users = sorted(kapyland_db.items(), key=lambda x: x[1]['weight'], reverse=True)
    msg = "🏆 **ЗАЛА СЛАВИ ТА ОЖИРІННЯ** 🏆\n\n"
    for i, (uid, info) in enumerate(sorted_users[:10]):
        name = info.get("kapy_name", "Щось жирне")
        weight = info.get("weight", 0)
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🐾"
        msg += f"{medal} {name}: **{weight}кг**\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in kapyland_db:
        k = kapyland_db[user_id]
        await update.message.reply_text(f"📊 Капібара **{k['kapy_name']}** важить **{k['weight']}кг**. 🌿")
    else:
        await update.message.reply_text("💨 У тебе немає капібари.")

async def delete_kapy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in kapyland_db:
        del kapyland_db[user_id]
        save_data(kapyland_db)
        await update.message.reply_text("🌊 Твоя капібара пішла навіки купатися в теплі джерела. Тепер ти зовсім один. 🧘‍♂️")
    else:
        await update.message.reply_text("❔ Тут нема чого видаляти.")

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    TOKEN = os.environ.get("BOT_TOKEN")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("name", set_name))
    application.add_handler(CommandHandler("feed", feed))
    application.add_handler(CommandHandler("top", leaderboard))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("delete", delete_kapy))
    application.run_polling()

if __name__ == "__main__":
    kapyland_db = load_data()
    main()