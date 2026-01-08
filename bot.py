import os
import random
import threading
import math
import pymongo
import pytz
import asyncio
from flask import Flask
from datetime import datetime, time as dt_time # Імпортуємо клас datetime і перейменовуємо клас time
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.helpers import escape_markdown

# ===================== VERSION INFO =====================
VERSION = "1.0.1"
CHANGELOG = """
• Додано тестову систему боїв
• Додано покарання за неприйнятну лексику
• Додано кілька пасхалок
"""
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
    # Використовуємо часовий пояс Києва, щоб дата не зміщувалася вночі
    tz = pytz.timezone("Europe/Kyiv")
    return datetime.now(tz).strftime("%Y-%m-%d")

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
    
    chat_id = str(update.effective_chat.id)
    stats_col.update_one(
        {"chat_id": chat_id, "date": today()},
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
    raw_name = " ".join(context.args)[:30]
    
    if not raw_name:
        await update.message.reply_text("📝 Пиши: `/name Ім'я`", parse_mode="Markdown")
        return

    u = users_col.find_one({"_id": uid})
    used_eggs = u.get("used_easter_eggs", []) # Список уже використаних бонусів
    
        # Гігантський список для фільтрації (UA + EN)
    BAD_WORDS = [
        # Українська та суржик
        "хуй", "хуя", "хуєм", "хуї", "пізда", "пізду", "піздєц", "єблан", "єбать", 
        "в’їбати", "виїбони", "сука", "сучка", "курва", "мудак", "мудило", "гандон", 
        "чмо", "лох", "підор", "підарас", "блєді", "бля", "блядь", "блєть", "заїбав", 
        "похуй", "нахуй", "піхуй", "отпіздити", "манда", "єбало", "їбало", "шльондра", 
        "лярва", "падла", "стерво", "виродок", "уєбан", "уєбище", "дрючити", "хер", 
        "хєрня", "дрочити", "сцикун", "гівно", "лайно", "дупа", "срака", "жертва аборту",

        # Англійська (основні та сленг)
        "fuck", "fucking", "fucker", "shit", "shitty", "bullshit", "ass", "asshole", 
        "bitch", "bastard", "dick", "cock", "pussy", "cunt", "faggot", "nigger", 
        "retard", "slut", "whore", "motherfucker", "dumbass", "cum", "semen", 
        "deepshit", "jackass", "prick", "wanker", "twat", "douche", "douchebag",
        "bollocks", "crap", "piss", "scum"
    ]
    EASTER_EGGS = {
        "Труп": 5.0, "Політех": -15.0, "Гачібара": 20.0,
        "Капібара": 10.0, "Тетерів": 10.0, "Розробник": 1.0,
        "Тарас": 5.0, "Славік": 5.0, "Саша": 5.0, "Андрій": 5.0,
        "Квас": 20.0, "Stardew valley": 5.0
    }

    penalty_weight = 0.0
    bonus_weight = 0.0
    status_msg = ""
    egg_to_register = None

    # 1. Штраф за мати (працює ЗАВЖДИ)
    if any(bad.lower() in raw_name.lower() for bad in BAD_WORDS):
        penalty_weight = -5.0
        status_msg += f"\n🤬 **Податок на лайку:** -5кг."

    # 2. Бонус за пасхалку (працює ОДИН РАЗ на кожне слово)
    for egg_name, weight in EASTER_EGGS.items():
        if raw_name.lower() == egg_name.lower():
            if egg_name not in used_eggs:
                bonus_weight = weight
                egg_to_register = egg_name
                status_msg += f"\n✨ Ого! Легендарне ім'я додало тобі **{bonus_weight}кг**!"
            else:
                status_msg += f"\n💡 Ти вже отримувала бонус за ім'я '{egg_name}', вдруге не спрацює, хитродупа капібара!"
            break

    safe_name = escape_markdown(raw_name, version=2)
    total_change = bonus_weight + penalty_weight
    
    # 3. Оновлення бази
    update_ops = {
        "$set": {"kapy_name": safe_name},
        "$inc": {"weight": total_change}
    }
    
    # Якщо була нова пасхалка, додаємо її в список використаних
    if egg_to_register:
        update_ops["$addToSet"] = {"used_easter_eggs": egg_to_register}

    users_col.update_one({"_id": uid}, update_ops)

    await update.message.reply_text(
        f"✅ Тепер капібару звати **{safe_name}**.{status_msg}",
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

async def judgment_day(update: Update | None, context: ContextTypes.DEFAULT_TYPE):
    is_auto = update is None
    chats = users_col.distinct("chats") if is_auto else [str(update.effective_chat.id)]

    for c_id in chats:
        users = list(users_col.find({"chats": c_id}))
        
        # Перевірка на кількість капібар
        if len(users) < 2:
            if not is_auto:
                await update.message.reply_text("⚖️ Судний день скасовано: у чаті має бути хоча б 2 капібари.")
            continue

        # Вибір ефекту всередині циклу для кожного чату окремо
        effect = random.choice([
            "усереднення", "голодомор", "урожай", "сповідь", 
            "гнів богів", "хрест", "святе випробування",
            "кара вавилону", "піст", "непорочне зачаття"
        ])

        msg = f"⚡️ **СУДНИЙ ДЕНЬ: {effect.upper()}** ⚡️\n"

        # УСІ ефекти мають бути всередині циклу (з відступом)
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
            msg += "🛡 Благословення забрані огами щоб перевірити капі на міцність."

        elif effect == "хрест":
            t = random.choice(users)
            user_curses = t.get("curses", [])
            if user_curses:
                c = random.choice(user_curses)
                users_col.update_one(
                    {"_id": t["_id"]},
                    {"$pull": {"curses": c}, "$addToSet": {"eternal_curses": c}},
                )
                msg += f"☦️ Прокляття **{c}** стало довічним для {t['kapy_name']}."
            else:
                msg += "🕊 Обрана капібара не мала проклять, тому боги її помилували."

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
            msg += "🌀 Ефекти перемішані між усіма гравцями. Вакханалія!"

        elif effect == "піст":
            sorted_u = sorted(users, key=lambda x: x["weight"])
            thin, fat = sorted_u[0], sorted_u[-1]
            users_col.update_one({"_id": thin["_id"]}, {"$inc": {"weight": 100}})
            users_col.update_one({"_id": fat["_id"]}, {"$mul": {"weight": 0.8}})
            msg += f"🥖 Скромна {thin['kapy_name']} отримала +20кг, а товстун {fat['kapy_name']} втратив 20% ваги."

        elif effect == "непорочне зачаття":
            t = random.choice(users)
            new_name = f"Святий {t['kapy_name']}"
            users_col.update_one({"_id": t["_id"]}, {"$set": {"kapy_name": new_name}})
            msg += f"👼 {t['kapy_name']} тепер носить титул **{new_name}**."

        elif effect == "гнів богів":
            t = random.choice(users)
            users_col.delete_one({"_id": t["_id"]})
            msg += f"🔥 {t['kapy_name']} була стерта з буття за гріхи господаря. Або просто вони тицьнули не ту кнопку"

        # Відправка повідомлення для конкретного чату
        try:
            await context.bot.send_message(chat_id=c_id, text=msg, parse_mode="Markdown")
        except Exception as e:
            print(f"Помилка відправки в чат {c_id}: {e}")
            continue

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
        {
            "name": "Шоколадка Рошен",
            "desc": "Солодка."
        },
        {
            "name": "Бурулька",
            "desc": "Геніталії сніговика."
        }
    ],

    "Rare": [
        {
            "name": "Камінь",
            "desc": "Має неймовірну аеродинаміку"
        },
        {
            "name": "Диплом",
            "desc": "Спочатку ти страждав заради нього, а тепер твій ворог."
        }
    ],

    "Epic": [
        {
            "name": "Самогон»",
            "desc": "По секретному рецепту діда."
        },
        {
            "name": "Кувалда",
            "desc": "Терпи, терпець тебе шліфує. І додатково трощить череп..."
        }
    ],

    "Legendary": [
        {
            "name": "Кішчяче життя",
            "desc": "По старій дружбі твій друг кіт подарував одне з його життів"
        },
        {
            "name": "Чайний патик",
            "desc": "Зібравши в собі аромат та ярлики всіх чаїв світу робить тебе непереможним"
        }
    ]
}

    uid = str(update.effective_user.id)
    u = users_col.find_one({"_id": uid})
    
    cost = 10.0  # Ціна однієї спроби — 20 кг
    
    if u.get("weight", 0) < cost + 5.0: # Залишаємо мінімум 5кг, щоб не вбити капібару
        await update.message.reply_text(
            f"❌ Твоя капібара занадто худа для жертвоприношення!\n"
            f"Потрібно мінімум **{cost + 5.0}кг**, а у тебе {u['weight']}кг."
        )
        return

    # Анімація казино
    msg = await update.message.reply_text("🎰 **ЖЕРТВОПРИНОШЕННЯ ВАГИ...**")
    
    r = random.random()

    if r < 0.02:
        rarity = "Legendary"   # 2%
    elif r < 0.10:
        rarity = "Epic"        # 8%
    elif r < 0.30:
        rarity = "Rare"        # 20%
    else:
        rarity = "Common"      # 70%


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

import random
import asyncio
import time
from telegram import Update
from telegram.ext import ContextTypes

WEAPONS = {
    "Шоколадка Рошен": {
        "text": "посадила підшлункову",
        "hit_bonus": 0.05
    },
    "Бурулька": {
        "text": "колола бурулькою",
        "hit_bonus": 0.07
    },
    "Камінь": {
        "text": "кинула і розвалила голову",
        "hit_bonus": 0.1
    },
    "Диплом": {
        "text": "удар дипломом (хоч тут згодився)",
        "hit_bonus": 0.15
    },
    "Самогон": {
        "text": "кастанула цироз печінки",
        "hit_bonus": 0.1,
        "effect": "memory"
    },
    "Кувалда": {
        "text": "розвалила голову кувалдою",
        "hit_bonus": 0.1,
        "effect": "stun"
    },
    "Кішчяче життя": {
        "text": "додаткове життя від котика!",
        "hit_bonus": 0.1
    },
    "Чайний патик": {
        "text": "зробила перший удар з силою чаю",
        "hit_bonus": 0.25,
        "first_strike": True
    }
}

async def fight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update)

    uid = str(update.effective_user.id)

    if not update.message.reply_to_message:
        await update.message.reply_text("🥊 Відповідай `/fight` на повідомлення опонента!")
        return

    target_id = str(update.message.reply_to_message.from_user.id)
    if uid == target_id:
        await update.message.reply_text("🍎 Неможливо битися із самим собою.")
        return

    # анти-абʼюз по часу
    if time.time() - update.message.reply_to_message.date.timestamp() > 90:
        await update.message.reply_text("⌛ Це повідомлення занадто старе.")
        return

    u1 = users_col.find_one({"_id": uid})
    u2 = users_col.find_one({"_id": target_id})

    if not u2:
        await update.message.reply_text("👤 Ворог не має капібари.")
        return

    now = time.time()
    if now - u1.get("last_fight", 0) < 60:
        await update.message.reply_text("⏳ Капібара ще відновлюється.")
        return

    if u1.get("in_fight") or u2.get("in_fight"):
        await update.message.reply_text("⚠️ Хтось уже в бою.")
        return

    users_col.update_one({"_id": uid}, {"$set": {"in_fight": True, "last_fight": now}})
    users_col.update_one({"_id": target_id}, {"$set": {"in_fight": True}})

    try:
        # HP
        hp1 = hp2 = 3
        name1, name2 = u1["kapy_name"], u2["kapy_name"]

        a1 = list(u1.get("artifacts", []))
        a2 = list(u2.get("artifacts", []))

        w1 = random.choice(a1) if a1 else None
        w2 = random.choice(a2) if a2 else None

        skip1 = skip2 = False
        first_strike_done = set()

        battle_msg = await update.message.reply_text(
            f"⚔️ **БІЙ ПОЧАТО!**\n\n"
            f"🟢 {name1}: ❤️❤️❤️\n"
            f"🔴 {name2}: ❤️❤️❤️",
            parse_mode="Markdown"
        )

        for round_num in range(1, 10):
            await asyncio.sleep(3)

            attacker_is_1 = round_num % 2 != 0
            attacker_name = name1 if attacker_is_1 else name2
            defender_name = name2 if attacker_is_1 else name1
            weapon = w1 if attacker_is_1 else w2

            if attacker_is_1 and skip1:
                skip1 = False
                continue
            if not attacker_is_1 and skip2:
                skip2 = False
                continue

            hit_chance = 0.5
            text = ""

            if weapon and weapon in WEAPONS:
                hit_chance += WEAPONS[weapon].get("hit_bonus", 0)

            if random.random() < hit_chance:
                if attacker_is_1:
                    hp2 -= 1
                else:
                    hp1 -= 1

                if weapon and weapon in WEAPONS:
                    text = f"💥 **{attacker_name}** {WEAPONS[weapon]['text']}!"
                else:
                    text = f"💥 **{attacker_name}** атакувала лапами!"

                # ефекти
                effect = WEAPONS.get(weapon, {}).get("effect")
                if effect == "memory" and random.random() < 0.25:
                    skip2 = attacker_is_1
                    skip1 = not attacker_is_1
                    text += "\n🧠 Памʼять суперника затьмарена!"

                if effect == "stun" and random.random() < 0.2:
                    skip2 = attacker_is_1
                    skip1 = not attacker_is_1
                    text += "\n🌀 Суперник приголомшений!"

                if WEAPONS.get(weapon, {}).get("first_strike") and weapon not in first_strike_done:
                    first_strike_done.add(weapon)
                    if attacker_is_1:
                        hp2 -= 1
                    else:
                        hp1 -= 1
                    text += "\n⚡ ПЕРШЕ РІШЕННЯ — подвійний удар!"

            else:
                text = f"💨 **{attacker_name}** промахнулася."

            hp_bar1 = "❤️" * max(0, hp1) + "🖤" * (3 - max(0, hp1))
            hp_bar2 = "❤️" * max(0, hp2) + "🖤" * (3 - max(0, hp2))

            await battle_msg.edit_text(
                f"🏟 **Раунд {round_num}**\n\n{text}\n\n"
                f"🟢 {name1}: {hp_bar1}\n"
                f"🔴 {name2}: {hp_bar2}",
                parse_mode="Markdown"
            )

            if hp1 <= 0 or hp2 <= 0:
                break

        winner_id, winner_name, loser_id, loser_name = (
            (uid, name1, target_id, name2) if hp1 > hp2
            else (target_id, name2, uid, name1)
        )

        users_col.update_one({"_id": winner_id}, {"$inc": {"weight": 0.5}})
        users_col.update_one({"_id": loser_id}, {"$inc": {"weight": -0.5}})

        await battle_msg.edit_text(
            f"🏆 **ПЕРЕМОГА!**\n\n"
            f"Переможець: **{winner_name}** (+0.5кг)\n"
            f"Переможений: **{loser_name}** (-0.5кг)",
            parse_mode="Markdown"
        )

    finally:
        users_col.update_one({"_id": uid}, {"$set": {"in_fight": False}})
        users_col.update_one({"_id": target_id}, {"$set": {"in_fight": False}})

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

async def updategame(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def audit_names(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Твій гігантський список (можна винести окремо)
    BAD_WORDS = [
        "хуй", "хуя", "хуєм", "хуї", "пізда", "пізду", "піздєц", "єблан", "єбать", 
        "сука", "сучка", "курва", "мудак", "мудило", "гандон", "чмо", "лох", "підор", 
        "підарас", "бля", "блядь", "заїбав", "похуй", "нахуй", "єбало", "їбало",
        "fuck", "fucking", "shit", "asshole", "bitch", "bastard", "dick", "cock", 
        "pussy", "cunt", "motherfucker", "cum" # ... і так далі
    ]

    users = list(users_col.find({}))
    fined_count = 0
    total_fines = 0.0
    report = "🧹 **РЕВІЗІЯ ІМЕН ЗАВЕРШЕНА**\n\n"

    for u in users:
        kapy_name = u.get("kapy_name", "").lower()
        # Очищуємо ім'я від символів для жорсткої перевірки (щоб не обійшли через "х.у.й")
        clean_name = "".join(char for char in kapy_name if char.isalnum())
        
        if any(bad in clean_name for bad in BAD_WORDS):
            # Штрафуємо на 5 кг
            users_col.update_one(
                {"_id": u["_id"]},
                {"$inc": {"weight": -5.0}}
            )
            fined_count += 1
            total_fines += 5.0
            report += f"⚠️ **{u['tg_name']}** ({u['kapy_name']}): -5кг\n"

    if fined_count > 0:
        report += f"\n📉 Разом оштрафовано: **{fined_count}** капібар."
        report += f"\n⚖️ Загальний прибуток богів: **{total_fines}кг**."
    else:
        report += "😇 Всі капібари чисті перед законом."

    await update.message.reply_text(report, parse_mode="Markdown")

async def notify_update(application: Application):
    # Отримуємо унікальні ID чатів з бази
    chats = users_col.distinct("chats")
    
    text = (
        f"🚀 **Kapyland оновлено до v{VERSION}**\n\n"
        f"**Що нового:**\n{CHANGELOG}\n\n"
        f"🥗 /feed — Годувати капібару"
    )

    for c_id in chats:
        try:
            # Відправляємо повідомлення
            await application.bot.send_message(
                chat_id=c_id, 
                text=text, 
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Не вдалося сповістити чат {c_id}: {e}")

# ===================== RUN =====================

def main():
    threading.Thread(target=run_flask, daemon=True).start()

    # Створюємо додаток
    app_tg = Application.builder().token(os.environ["BOT_TOKEN"]).build()

    # Налаштовуємо час (наприклад, 22:00 за Києвом)
    job_queue = app_tg.job_queue
    kyiv_tz = pytz.timezone("Europe/Kyiv")
    # 1. Надобраніч (щодня о 19:50)
    job_queue.run_daily(
        send_goodnight, 
        time=dt_time(hour=19, minute=50, tzinfo=kyiv_tz)
    )

    # 2. Судний День (кожні 4 дні о 20:35)
    job_queue.run_repeating(
        lambda ctx: judgment_day(None, ctx), # Передаємо None замість update
        interval=345600, 
        first=dt_time(hour=20, minute=35, tzinfo=kyiv_tz)
    )

    app_tg.post_init = notify_update

    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(CommandHandler("name", set_name))
    app_tg.add_handler(CommandHandler("feed", feed))
    app_tg.add_handler(CommandHandler("fight", fight))
    app_tg.add_handler(CommandHandler("stats", stats))
    app_tg.add_handler(CommandHandler("top", leaderboard))
    app_tg.add_handler(CommandHandler("delete", delete_kapy))
    app_tg.add_handler(CommandHandler("advice", advice))
    app_tg.add_handler(CommandHandler("update", updategame))
    app_tg.add_handler(CommandHandler("audit", audit_names))
    app_tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_messages))

    app_tg.run_polling()

if __name__ == "__main__":
    main()
