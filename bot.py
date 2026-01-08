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
import datetime
import pytz # Додай у requirements.txt, щоб часовий пояс працював чітко

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
chat_state_col = db["chat_state"]

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
    "Вона їсть, щоб забути про порожнечу всередині себе. Як і ти... 🕳",
    "Сподіваюся, ти теж так дбаєш про власне здоров'я, як про цього стронгмена... 🧂",
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

def is_sunday():
    return datetime.now().weekday() == 6

def week_id():
    return datetime.now().strftime("%Y-%W")

def all_fed_today(chat_id):
    users = list(users_col.find({"chats": chat_id}))
    if not users:
        return False
    return all(u.get("last_feed_date") == today() for u in users)

def sanitize_weight(w, curses):
    if "Сліпота" in curses:
        return "[ПРИХОВАНО]"
    txt = f"{round(w, 2)}"
    if "Дислексія" in curses:
        l = list(txt)
        random.shuffle(l)
        txt = "".join(l)
    return f"**{txt}кг**"

# ===================== DAILY EFFECTS =====================

def daily_effects(u):
    if u.get("last_daily_effect") == today():
        return []

    log = []

    chance = 0.1
    # 10% new blessing
    if random.random() < chance:
        avail = list(set(BLESSINGS) - set(u["blessings"]))
        if avail:
            b = random.choice(avail)
            u["blessings"].append(b)
            desc = BLESSINGS.get(b, "")
            log.append(f"✨ Отримано благословення: {b} — {desc}")

    # 10% lose blessing
    if u["blessings"] and random.random() < 0.1:
        b = random.choice(u["blessings"])
        u["blessings"].remove(b)
        desc = BLESSINGS.get(b, "")
        log.append(f"💔 Втрачено благословення: {b} — {desc}")

    # 10% new curse
    if random.random() < chance:
        avail = list(set(CURSES) - set(u["curses"]) - set(u["eternal_curses"]))
        if avail:
            c = random.choice(avail)
            u["curses"].append(c)
            desc = CURSES.get(c, "")
            log.append(f"💀 Отримано прокляття: {c} — {desc}")

    # 10% lose curse
    if u["curses"] and random.random() < 0.1:
        c = random.choice(u["curses"])
        u["curses"].remove(c)
        desc = CURSES.get(c, "")
        log.append(f"🕊 Прокляття зникло: {c} — {desc}")

    users_col.update_one(
        {"_id": u["_id"]},
        {
            "$set": {
                "blessings": u["blessings"],
                "curses": u["curses"],
                "last_daily_effect": today(),
            }
        },
    )

    return log

# ===================== USER =====================

def ensure_user(update: Update):
    tg_user = update.effective_user
    uid = str(tg_user.id)
    cid = str(update.effective_chat.id)

    username = tg_user.username
    display_name = tg_user.full_name or "Безіменний смертний"

    u = users_col.find_one({"_id": uid})

    effects = []

    if not u:
        users_col.insert_one({
            "_id": uid,
            "tg_username": username,
            "tg_name": display_name,
            "kapy_name": "Безіменна булочка",
            "weight": 20.0,
            "last_feed_date": "",
            "last_daily_effect": "",
            "chats": [cid],
            "blessings": [],
            "curses": [],
            "eternal_curses": [],
            "history": [0.0],
        })
    else:
        users_col.update_one(
            {"_id": uid},
            {
                "$addToSet": {"chats": cid},
                "$set": {
                    "tg_username": username,
                    "tg_name": display_name,
                },
            },
        )
        u = users_col.find_one({"_id": uid})
        effects = daily_effects(u)

    return effects

# ===================== TRACK CHAT =====================
async def track_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    stats_col.update_one(
        {"chat_id": str(update.effective_chat.id), "date": today()},
        {"$inc": {"letters": len(update.message.text)}},
        upsert=True,
    )

    state = chat_state_col.find_one({"chat_id": c_id})
    if state and state.get("week") == week_id() and state.get("judged"):
        return

    chat_state_col.update_one(
        {"chat_id": c_id},
        {"$set": {"week": week_id(), "judged": True}},
        upsert=True,
    )

# ===================== COMMANDS =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update)
    u = users_col.find_one({"_id": str(update.effective_user.id)})

    if u["last_feed_date"] == "":
        story = random.choice(ORIGIN_STORIES)
        await update.message.reply_text(
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
    uid = str(update.effective_user.id)
    name = " ".join(context.args)
    
    if not name:
        await update.message.reply_text("📝 Пиши: `/name Ім'я`", parse_mode="Markdown")
        return

    # 1. Словник з секретними іменами та бонусами
    EASTER_EGGS = {
        "Труп": 5.0,
        "Політех": -15.0,
        "Гачібара": 20.0,
        "Капібара": 10.0,
        "Тетерів": 10.0,
        "Капібара": 10.0,
        "Розробник": 1.0  # символічний бонус
    }

    bonus_msg = ""
    bonus_weight = 0.0

    # 2. Перевірка на співпадіння (ігноруючи регістр)
    for egg_name, weight in EASTER_EGGS.items():
        if name.lower() == egg_name.lower():
            bonus_weight = weight
            bonus_msg = f"\n✨ Ого! Це легендарне ім'я додало тобі **{bonus_weight}кг**!"
            break

    # 3. Оновлюємо ім'я та додаємо вагу (якщо є бонус)
    users_col.update_one(
        {"_id": uid},
        {
            "$set": {"kapy_name": name},
            "$inc": {"weight": bonus_weight} # $inc додає значення до існуючого
        }
    )

    await update.message.reply_text(
        f"✅ Тепер цю купу хутра звати **{name}**.{bonus_msg}",
        parse_mode="Markdown"
    )

async def feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Завантажуємо користувача та чат
    u = users_col.find_one({"_id": str(update.effective_user.id)})
    c_id = str(update.effective_chat.id)

    # 1️⃣ Викликаємо daily_effects та показуємо ефекти в чаті
    effects = daily_effects(u)
    if effects:
        await update.message.reply_text("\n".join(effects), parse_mode="Markdown")

    # 2️⃣ Підвантажуємо користувача знову, щоб щойно отримані ефекти не впливали на сьогоднішній gain
    u = users_col.find_one({"_id": str(update.effective_user.id)})

    # 3️⃣ Перевірка, чи вже годували сьогодні
    if u["last_feed_date"] == today():
        await update.message.reply_text(random.choice(FEED_RESTRICTION_JOKES))
        return

    # 4️⃣ Обчислюємо приріст ваги
    gain = random.randint(1, 10) * 0.5
    log = ""

    if "Четверта стіна" in u["blessings"]:
        st = stats_col.find_one({"chat_id": c_id, "date": today()}) or {"letters": 10}
        bonus = round(math.log10(max(st["letters"], 10)) * 2) / 2
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
        elif r < 0.5:
            gain = 0

    if "Дієта" in u["curses"]:
        gain = 0

    if "Лудоман" in u["curses"]:
        gain += random.uniform(-10, 10)

    # 5️⃣ Вибираємо реакцію капібари
    if gain > 0:
        reaction = random.choice(EDGY_JOKES)
    elif gain < 0:
        reaction = random.choice(FAIL_MESSAGES)
    else:
        reaction = random.choice(EQUILIBRIUM_MESSAGES)

    # 6️⃣ Оновлюємо вагу користувача та історію приростів
    new_weight = max(1.0, round(u["weight"] * 2 + gain * 2) / 2)
    users_col.update_one(
        {"_id": u["_id"]},
        {
            "$set": {"weight": new_weight, "last_feed_date": today()},
            "$push": {"history": {"$each": [gain], "$slice": -5}},
        },
    )

    # 7️⃣ Відправляємо повідомлення про приріст і реакцію
    await update.message.reply_text(
        f"{log}🍊 Приріст: **{round(gain,2)}кг**\n"
        f"⚖️ Вага: {sanitize_weight(new_weight, u['curses'])}\n\n"
        f"_{reaction}_",
        parse_mode="Markdown",
    )

async def judgment_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c_id = str(update.effective_chat.id)
    users = list(users_col.find({"chats": c_id}))

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
            {"$set": {"kapy_name": f"Ісус {t['kapy_name']}"}},
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

    eternal = ", ".join(u.get("eternal_curses", [])) or "немає"

    await update.message.reply_text(
        f"📊 **{u['kapy_name']}**\n"
        f"⚖️ {sanitize_weight(u['weight'], u['curses'])}\n"
        f"✨ Благословення: {', '.join(u['blessings']) or 'немає'}\n"
        f"💀 Прокляття: {', '.join(u['curses']) or 'немає'}\n"
        f"⛓️ **Довічні кайдани:** {eternal}",
        parse_mode="Markdown",
    )

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c_id = str(update.effective_chat.id)
    top = users_col.find({"chats": c_id}).sort("weight", -1).limit(10)

    msg = "🏆 **ЗАЛ КАПІСЛАВИ** 🏆\n\n"

    for i, u in enumerate(top, start=1):
        tg = (
            f"{u['tg_name']}"
            if u.get("tg_name")
            else u.get("tg_username", "Невідомий")
        )

        weight_txt = sanitize_weight(u["weight"], u.get("curses", []))

        msg += (
            f"{i}. 🐾 **{u['kapy_name']}**"
            f"  ({tg}) - "
            f"{weight_txt}\n\n"
        )

    await update.message.reply_text(msg, parse_mode="Markdown")

async def advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Провіряємо чи юзер існує в базі
    ensure_user(update)
    
    CAPY_ADVICE = [
    "Ходять легенди, що капібара з гарним ім'ям може отримати дари від богів. Зазвичай...",
    "Ефекти (благословення та прокляття) можуть як з'явитися так і зникнути з шансом 10% після кожного твого годування",
    "Судний день настає кожні чотири дні, бо боги капібар далі не вміють рахувати" ]
    # Вибираємо рандомну пораду
    random_advice = random.choice(CAPY_ADVICE)
    
    # Відправляємо повідомлення
    await update.message.reply_text(
        f"📜 **Порада від Капібари:**\n\n_{random_advice}_",
        parse_mode="Markdown"
    )

async def delete_kapy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)

    if not context.args:
        await update.message.reply_text(
            "⚠️ **Це незворотній процес (капібара назавжди втратить довіру)**\n\n"
            "Якщо ти впевнений:\n"
            "`/delete YES`",
            parse_mode="Markdown",
        )
        return

    if context.args[0] != "YES":
        await update.message.reply_text("❌ Видалення скасовано.")
        return
    res = users_col.delete_one({"_id": uid})

    if res.deleted_count:
        await update.message.reply_text(
            "🌊 Твоя капібара пішла навіки купатися в теплі джерела.\n"
            "Цього разу — без повернення."
        )
    else:
        await update.message.reply_text("❔ Тут нема чого видаляти.")

async def gacha(update: Update, context: ContextTypes.DEFAULT_TYPE):

    GACHA_ITEMS = {
    "Common": [
        {"name": "Дерев'яний патик"}
    ],
    "Rare": [
        {"name": "Фотокамера"},
    ],
    "Legendary": [
       {"name": "Договоняк"}
    ]
}

    uid = str(update.effective_user.id)
    u = users_col.find_one({"_id": uid})
    
    cost = 20.0  # Ціна однієї спроби — 20 кг
    
    if u.get("weight", 0) < cost + 5.0: # Залишаємо мінімум 5кг, щоб не вбити капібару
        await update.message.reply_text(
            f"❌ Твоя капібара занадто худа для жертвоприношення!\n"
            f"Потрібно мінімум **{cost + 5.0}кг**, а у тебе {u['weight']}кг."
        )
        return

    # Анімація казино
    msg = await update.message.reply_text("🎰 **ЖЕРТВОПРИНОШЕННЯ ВАГИ...**")
    
    # Визначаємо рарність
    r = random.random()
    if r < 0.07: rarity = "Legendary"
    elif r < 0.25: rarity = "Rare"
    else: rarity = "Common"

    item = random.choice(GACHA_ITEMS[rarity])
    
    # Оновлення бази: мінусуємо вагу, додаємо артефакт
    users_col.update_one(
        {"_id": uid},
        {
            "$inc": {"weight": -cost},
            "$addToSet": {"artifacts": item["name"]} # Додаємо в унікальний список артефактів
        }
    )

    await msg.edit_text(
        f"🎰 **ГАЗИНО КАПІБАР**\n"
        f"📉 Витрачено: **-{cost}кг** ваги\n\n"
        f"✨ Випав артефакт: **[{rarity}] {item['name']}**\n"
        f"📜 Ефект: _{item['desc']}_",
        parse_mode="Markdown"
    )

GOODNIGHT_JOKES = [
    "намагається напрограмувати цей клятий бот"
]

async def send_goodnight(context: ContextTypes.DEFAULT_TYPE):
    # Отримуємо всі унікальні чати
    chats = users_col.distinct("chats")
    joke = random.choice(GOODNIGHT_JOKES)
    text = f"🌙 **Надобраніч від капібари, яка {joke}.**"
    
    for chat_id in chats:
        try:
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
        except Exception as e:
            print(f"Помилка надсилання в {chat_id}: {e}")

async def update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Отримуємо всіх користувачів
    users = list(users_col.find({}))
    count = 0

    for u in users:
        old_weight = u.get("weight", 20.0)
        # Магічна формула округлення до 0.5
        new_weight = round(old_weight * 2) / 2
        
        # Оновлюємо в базі
        users_col.update_one(
            {"_id": u["_id"]},
            {"$set": {"weight": new_weight}}
        )
        count += 1

    await update.message.reply_text(f"✅ Магічне вирівнювання завершено!\nОновлено капібар: **{count}**\nТепер всі ваги кратні 0.5 кг.")

# ===================== RUN =====================

def main():
    threading.Thread(target=run_flask, daemon=True).start()

    # Створюємо додаток
    app_tg = Application.builder().token(os.environ["BOT_TOKEN"]).build()

    # Налаштовуємо час (наприклад, 22:00 за Києвом)
    job_queue = app_tg.job_queue
    kyiv_tz = pytz.timezone("Europe/Kyiv")
    # 1. Надобраніч (щодня о 22:00)
    job_queue.run_daily(
        send_goodnight, 
        time=datetime.time(hour=19, minute=50, tzinfo=kyiv_tz)
    )

    # 2. Судний День (кожні 4 дні о 20:00)
    # interval = 345600 секунд (4 дні)
    job_queue.run_repeating(
        judgment_day, 
        interval=345600, 
        first=datetime.time(hour=19, minute=51, tzinfo=kyiv_tz)
    )

    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(CommandHandler("name", set_name))
    app_tg.add_handler(CommandHandler("feed", feed))
    app_tg.add_handler(CommandHandler("judgment", judgment_day))
    app_tg.add_handler(CommandHandler("stats", stats))
    app_tg.add_handler(CommandHandler("top", leaderboard))
    app_tg.add_handler(CommandHandler("delete", delete_kapy))
    app_tg.add_handler(CommandHandler("advice", advice))
    app_tg.add_handler(CommandHandler("update", update))
    app_tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_messages))

    app_tg.run_polling()

if __name__ == "__main__":
    main()
