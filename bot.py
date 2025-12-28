import os
import random
import threading
import math
import pymongo
from datetime import datetime
from flask import Flask
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.helpers import escape_markdown

# ===================== WEB =====================

app = Flask(__name__)

@app.route("/")
def home():
    return "🐾 Kapyland: Divine Edition is running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ===================== DB =====================

client = pymongo.MongoClient(os.environ.get("MONGO_URI"))
db = client["kapyland_db"]
users_col = db["users"]
stats_col = db["chat_stats"]

# ===================== DATA =====================

ORIGIN_STORIES = [
    "📦 Ти знайшов заклеєну коробку біля смітника. Всередині була вона — 20 кілограмів чистої апатії.",
    "🃏 Ти виграв цю капібару в карти у привокзального безхатька. Він виглядав щасливим, коли йшов геть...",
    "🌑 Вона просто з'явилася у твоїй кімнаті посеред ночі. Ти не знаєш як, але тепер ти мусиш її годувати.",
    "🏢 Ти купив її через оголошення в даркнеті в розділі 'Помилки природи'. Доставка була безкоштовною.",
    "🎒 Ти йшов лісом і побачив, як капібара намагається вкрасти чийсь рюкзак. Тепер вона твоя проблема.",
    "🛸 Яскраве світло, звук працюючого пилосмока, і ось вона — висаджена інопланетянами прямо тобі під двері.",
    "💳 Ти випадково натиснув 'Купити зараз' на сумнівному сайті під час безсоння. Тепер у тебе мінус на карті і плюс капібара.",
    "🕵️ Тобі передали її люди в чорних плащах, прошепотівши: 'Бережи її, вона знає забагато'.",
]

EDGY_JOKES = [
    "Ще один шматок, і вона вибухне, забравши з собою цей чат і твоє майбутнє 🧨",
    "Ще один шматочок, і вона пригравітує Місяць до Землі 🌌",
    "Твоя капібара виглядає так, ніби вона щойно з'їла чиїсь надії та мрії 💭",
    "Твоя капібара стала на крок ближче до ідеальної форми кулі ⚪️",
    "Вона їсть, щоб забути про порожнечу ventilated всередині. Як і ти... 🕳",
    "Сподіваюся, ти теж так дбаєш про власне здоров'я, як про цю товстуню... 🧂",
    "Вона стає настільки великою, що скоро держава забере її на прогодівлю ЗСУ 🫡",
    "Це не вага, це накопичена ненависть до людства 😈",
    "Твоя капібара бачила пекло, і сказала, що там недостатньо апельсинів 🍊",
    "Вона занадто розслаблена для того, хто перебуває в одному кроці від проблем із серцем 💧",
]

FAIL_MESSAGES = [
    "Її знудило твоїми АТБшними апельсинами та отримала в бонус діарею 🤢",
    "Вона впала в екзистенційну кризу від останніх новин і відмовилася їсти 📺",
    "Капібарка вирішила продати частину душі. Хто ж знав що вона теж має вагу? ⚖️",
    "Твоя капібара влаштувала бойкот через твою поведінку останнім часом 🪧",
    "У неї випали зуби від твого розбещеного раціону. Тепер вона харчується тільки енергією сонця і чаю 🍵",
]

EQUILIBRIUM_MESSAGES = [
    "Капібара на відміну від тебе пішла мацати траву 🌱",
    "Сила волі мандаринки виявилася сильніша і вона не перетравилася 🍊",
    "Вона проігнорувала твої намагання. Вона вища за це 🏔",
    "Капібарка змерзла і вийшла в нуль, спаливши калорії ❄️",
]

FEED_RESTRICTION_JOKES = [
    "🚫 Гроші закінчилися, апельсини в кредит більше не дають",
    "🚫 Ветеринар заборонив її годувати сьогодні, бо діагностував ожиріння, діабет та критичне мислення",
    "🚫 Капібара оголосила ситу сієсту. Приходь завтра",
    "🚫 Твоя кредитка заблокована через підозрілу активність у відділі фруктів",
    "🚫 Твоя капібара стала більша за синього кита і була забрана морськими біологами. Повернуть завтра",
]

BLESSINGS = {
    "Кум в податковій": "10% від прибутку маси інших капі",
    "Всі за одного і один за всіх": "якщо капі втрачає масу то всі інші худнуть з нею і навпаки",
    "Вічна фієста": "не може схуднути",
    "Повільний метаболізм": "набирає в х1.5 раза більше",
    "Фібоначчі": "кожен день додається прибуток нині + вчора",
    "Четверта стіна": "приріст рівний логарифму літер в чаті",
}

CURSES = {
    "Злий робін гуд": "передає 5 кг від найхудішої капібари до випадкової іншої",
    "Дієта": "маса залишається однакова",
    "Лудоман": "кожен день самовільно проводить жертвоприношення (в розробці)",
    "Ні собі ні людям": "всі втрачають 10% від прибутку",
    "Сліпота": "дані, приріст капі приховується",
    "Дислексія": "числа приросту переставляються випадково",
}

# ===================== HELPERS =====================

def today():
    return datetime.now().strftime("%Y-%m-%d")

def ensure_user(update: Update):
    u_id = str(update.effective_user.id)
    c_id = str(update.effective_chat.id)

    user = users_col.find_one({"_id": u_id})
    if not user:
        users_col.insert_one({
            "_id": u_id,
            "kapy_name": "Безіменна булочка",
            "weight": 20.0,
            "last_feed_date": "",
            "chats": [c_id],
            "blessings": [],
            "curses": [],
            "eternal_curses": [],
            "history": [0.0],
            "full_name": update.effective_user.full_name,
        })
    else:
        users_col.update_one(
            {"_id": u_id},
            {"$addToSet": {"chats": c_id}},
        )

def sanitize_weight(w, curses):
    if "Сліпота" in curses:
        return "[ПРИХОВАНО]"
    txt = f"{round(w, 2)}"
    if "Дислексія" in curses:
        l = list(txt)
        random.shuffle(l)
        txt = "".join(l)
    return f"**{txt}кг**"

# ===================== TRACK CHAT =====================

async def track_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    stats_col.update_one(
        {"chat_id": str(update.effective_chat.id), "date": today()},
        {"$inc": {"letters": len(update.message.text)}},
        upsert=True,
    )

# ===================== COMMANDS =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update)
    u = users_col.find_one({"_id": str(update.effective_user.id)})

    if u["last_feed_date"] == "":
        story = random.choice(ORIGIN_STORIES)
        await update.message.reply_text(
            f"✨ **Вітаємо у Kapyland!** ✨\n\n"
            f"{story}\n\n"
            f"🍊 Зараз вона важить **20кг**.\n"
            f"🏷️ Дай їй ім'я: `/name Кличка`.\n"
            f"🥗 Годуй через /feed!",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text("🐾 Твоя капібара все ще тут. Перевір /stats.")

async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update)
    name = " ".join(context.args)
    if not name:
        await update.message.reply_text("📝 Пиши: `/name Ім'я`", parse_mode="Markdown")
        return
    users_col.update_one(
        {"_id": str(update.effective_user.id)},
        {"$set": {"kapy_name": name}},
    )
    await update.message.reply_text(f"✅ Тепер цю купу хутра звати **{name}**.")

async def feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update)
    u = users_col.find_one({"_id": str(update.effective_user.id)})
    c_id = str(update.effective_chat.id)

    if u["last_feed_date"] == today():
        await update.message.reply_text(random.choice(FEED_RESTRICTION_JOKES))
        return

    gain = round(random.uniform(0.5, 5.0), 2)
    log = ""

    if "Четверта стіна" in u["blessings"]:
        st = stats_col.find_one({"chat_id": c_id, "date": today()}) or {"letters": 10}
        bonus = round(math.log10(max(st["letters"], 10)), 2)
        gain += bonus
        log += f"📺 Четверта стіна +{bonus}кг\n"

    if "Повільний метаболізм" in u["blessings"]:
        gain *= 1.5

    if "Фібоначчі" in u["blessings"]:
        gain += u["history"][-1]

    if "Вічна фієста" not in u["blessings"]:
        r = random.random()
        if r < 0.4:
            gain = -gain
            log += random.choice(FAIL_MESSAGES) + "\n"
        elif r < 0.5:
            gain = 0
            log += random.choice(EQUILIBRIUM_MESSAGES) + "\n"

    if "Дієта" in u["curses"]:
        gain = 0

    if "Лудоман" in u["curses"]:
        gain += random.uniform(-10, 10)

    new_weight = max(1.0, round(u["weight"] + gain, 2))

    users_col.update_one(
        {"_id": u["_id"]},
        {
            "$set": {"weight": new_weight, "last_feed_date": today()},
            "$push": {"history": {"$each": [gain], "$slice": -5}},
        },
    )

    await update.message.reply_text(
        f"{log}🍊 Приріст: **{round(gain,2)}кг**\n"
        f"⚖️ Вага: {sanitize_weight(new_weight, u['curses'])}\n\n"
        f"_{random.choice(EDGY_JOKES)}_",
        parse_mode="Markdown",
    )

async def judgment_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c_id = str(update.effective_chat.id)
    users = list(users_col.find({"chats": c_id}))

    if len(users) < 2:
        await update.message.reply_text("⚠️ Замало капібар для суду.")
        return

    effect = random.choice([
        "усереднення",
        "голодомор",
        "урожай",
        "сповідь",
        "святе випробування",
        "хрест",
        "кара вавилону",
        "піст",
        "непорочне зачаття",
        "гнів богів",
    ])

    msg = f"⚡️ **СУДНИЙ ДЕНЬ: {effect.upper()}** ⚡️\n"

    if effect == "усереднення":
        avg = round(sum(u["weight"] for u in users) / len(users), 2)
        users_col.update_many({"chats": c_id}, {"$set": {"weight": avg}})
        msg += f"⚖️ Всі зрівняні до **{avg}кг**."

    elif effect == "голодомор":
        t = random.choice(users)
        users_col.update_one({"_id": t["_id"]}, {"$mul": {"weight": 0.5}})
        msg += f"💀 {t['kapy_name']} втратила половину ваги."

    elif effect == "урожай":
        users_col.update_many({"chats": c_id}, {"$inc": {"weight": 50}})
        msg += "🌾 Благодать! +50кг кожній капібарі."

    elif effect == "сповідь":
        users_col.update_many({"chats": c_id}, {"$set": {"curses": []}})
        msg += "🙏 Всі прокляття знято."

    elif effect == "святе випробування":
        users_col.update_many({"chats": c_id}, {"$set": {"blessings": []}})
        msg += "🛡 Благословення забрані богами."

    elif effect == "хрест":
        t = random.choice(users)
        if t.get("curses"):
            c = random.choice(t["curses"])
            users_col.update_one(
                {"_id": t["_id"]},
                {"$pull": {"curses": c}, "$addToSet": {"eternal_curses": c}},
            )
            msg += f"☦️ Прокляття **{c}** стало довічним для {t['kapy_name']}."
        else:
            msg += "🕊 Ніхто не мав проклять."

    elif effect == "кара вавилону":
        all_b, all_c = [], []
        for u in users:
            all_b += u.get("blessings", [])
            all_c += u.get("curses", [])

        random.shuffle(all_b)
        random.shuffle(all_c)

        for u in users:
            users_col.update_one(
                {"_id": u["_id"]},
                {
                    "$set": {
                        "blessings": [all_b.pop()] if all_b else [],
                        "curses": [all_c.pop()] if all_c else [],
                    }
                },
            )
        msg += "🌀 Ефекти перемішані. Хаос."

    elif effect == "піст":
        sorted_u = sorted(users, key=lambda x: x["weight"])
        thin, fat = sorted_u[0], sorted_u[-1]
        users_col.update_one({"_id": thin["_id"]}, {"$inc": {"weight": 100}})
        users_col.update_one({"_id": fat["_id"]}, {"$mul": {"weight": 0.8}})
        msg += f"🥖 {thin['kapy_name']} +100кг, {fat['kapy_name']} на дієті."

    elif effect == "непорочне зачаття":
        t = random.choice(users)
        users_col.update_one(
            {"_id": t["_id"]},
            {"$set": {"kapy_name": f\"Ісус {t['kapy_name']}\"}},
        )
        msg += f"👼 {t['kapy_name']} стала священною."

    elif effect == "гнів богів":
        t = random.choice(users)
        users_col.delete_one({"_id": t["_id"]})
        msg += f"🔥 {t['kapy_name']} стерта з буття."

    await update.message.reply_text(msg, parse_mode="Markdown")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update)
    u = users_col.find_one({"_id": str(update.effective_user.id)})
    await update.message.reply_text(
        f"📊 **{escape_markdown(u['kapy_name'],2)}**\n"
        f"⚖️ {u['weight']}кг\n"
        f"✨ Благословення: {', '.join(u['blessings']) or 'немає'}\n"
        f"💀 Прокляття: {', '.join(u['curses']) or 'немає'}",
        parse_mode="MarkdownV2",
    )

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c_id = str(update.effective_chat.id)
    top = users_col.find({"chats": c_id}).sort("weight", -1).limit(10)
    msg = "🏆 **ТОП КАПІБАР** 🏆\n\n"
    for i, u in enumerate(top):
        msg += f"{i+1}. {u['kapy_name']} — **{u['weight']}кг**\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def delete_kapy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = users_col.delete_one({"_id": str(update.effective_user.id)})
    if res.deleted_count:
        await update.message.reply_text(
            "🌊 Твоя капібара пішла навіки купатися в теплі джерела. Тепер ти зовсім один. 🧘‍♂️"
        )
    else:
        await update.message.reply_text("❔ Тут нема чого видаляти.")

# ===================== RUN =====================

def main():
    threading.Thread(target=run_flask, daemon=True).start()

    app_tg = Application.builder().token(os.environ["BOT_TOKEN"]).build()

    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(CommandHandler("name", set_name))
    app_tg.add_handler(CommandHandler("feed", feed))
    app_tg.add_handler(CommandHandler("judgment", judgment_day))
    app_tg.add_handler(CommandHandler("stats", stats))
    app_tg.add_handler(CommandHandler("top", leaderboard))
    app_tg.add_handler(CommandHandler("delete", delete_kapy))
    app_tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_messages))

    app_tg.run_polling()

if __name__ == "__main__":
    main()
