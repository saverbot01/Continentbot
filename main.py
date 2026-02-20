import telebot
from telebot import types
import requests
import json
import os

# ====== BOT CONFIG ======
TOKEN = "8284519099:AAHY3JRVyjN3nQ7224IVBiq66cGDvEbJYnE"  # Telegram Bot Token
MAIN_ADMIN = 8213426436  # Сенинг ID
USERS_FILE = "users.json"
ADMINS_FILE = "admins.json"

bot = telebot.TeleBot(TOKEN)

# ====== LOAD USERS ======
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = []

# ====== LOAD ADMINS ======
if os.path.exists(ADMINS_FILE):
    with open(ADMINS_FILE, "r") as f:
        admins = json.load(f)
else:
    admins = [MAIN_ADMIN]

# ====== SAVE FUNCTIONS ======
def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def save_admins():
    with open(ADMINS_FILE, "w") as f:
        json.dump(admins, f)

# ====== GLOBAL ======
waiting_country = {}

# ====== /start ======
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id not in users:
        users.append(user_id)
        save_users()

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🌍 Европа", callback_data="Europe"),
        types.InlineKeyboardButton("🌏 Осиё", callback_data="Asia"),
    )
    markup.add(
        types.InlineKeyboardButton("🌎 Америка", callback_data="Americas"),
        types.InlineKeyboardButton("🌍 Африка", callback_data="Africa"),
    )

    bot.send_message(message.chat.id,
                     "Континентни танланг:",
                     reply_markup=markup)

# ====== CONTINENT CALLBACK ======
@bot.callback_query_handler(func=lambda call: True)
def continent_selected(call):
    waiting_country[call.from_user.id] = call.data
    bot.send_message(call.message.chat.id,
                     "Давлат номини рус ёки инглиз тилида ёзинг:")

# ====== COUNTRY INFO ======
@bot.message_handler(func=lambda message: message.from_user.id in waiting_country)
def country_info(message):
    continent = waiting_country[message.from_user.id]
    country_name = message.text

    url = f"https://restcountries.com/v3.1/name/{country_name}"
    response = requests.get(url)

    if response.status_code != 200:
        bot.send_message(message.chat.id, "Давлат топилмади ❌")
        return

    data = response.json()[0]

    if data.get("region") != continent:
        bot.send_message(message.chat.id,
                         "Бу давлат танланган континентга тегишли эмас ❌")
        return

    name = data['name']['common']
    capital = data.get('capital', ['Маълум эмас'])[0]
    population = "{:,}".format(data['population'])
    area = "{:,}".format(data['area'])
    currency = list(data.get('currencies', {}).keys())[0]
    flag = data['flags']['png']

    text = f"""
🌍 Давлат: {name}
🏙 Пойтахт: {capital}
👥 Аҳоли: {population}
📏 Майдон: {area} км²
💰 Валюта: {currency}
"""

    bot.send_photo(message.chat.id, flag, caption=text)

    del waiting_country[message.from_user.id]

# ====== /users ======
@bot.message_handler(commands=['users'])
def users_count(message):
    if message.from_user.id in admins:
        bot.send_message(message.chat.id,
                         f"Фойдаланувчилар сони: {len(users)}")
    else:
        bot.send_message(message.chat.id, "Сиз админ эмассиз ❌")

# ====== /admin ======
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id not in admins:
        bot.send_message(message.chat.id, "Рухсат йўқ ❌")
        return

    bot.send_message(message.chat.id,
"""
Admin panel:

/addadmin ID
/removeadmin ID
/admins
""")

# ====== /addadmin ======
@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    if message.from_user.id not in admins:
        return

    try:
        new_admin = int(message.text.split()[1])
        if new_admin not in admins:
            admins.append(new_admin)
            save_admins()
            bot.send_message(message.chat.id, "Admin қўшилди ✅")
        else:
            bot.send_message(message.chat.id, "Бу аллақачон админ")
    except:
        bot.send_message(message.chat.id,
                         "Тўғри формат: /addadmin 123456789")

# ====== /removeadmin ======
@bot.message_handler(commands=['removeadmin'])
def remove_admin(message):
    if message.from_user.id != MAIN_ADMIN:
        bot.send_message(message.chat.id,
                         "Фақат асосий админ ўчира олади ❌")
        return

    try:
        admin_id = int(message.text.split()[1])
        if admin_id in admins and admin_id != MAIN_ADMIN:
            admins.remove(admin_id)
            save_admins()
            bot.send_message(message.chat.id, "Admin ўчирилди ✅")
        else:
            bot.send_message(message.chat.id,
                             "Бундай админ йўқ")
    except:
        bot.send_message(message.chat.id,
                         "Тўғри формат: /removeadmin 123456789")

# ====== /admins ======
@bot.message_handler(commands=['admins'])
def list_admins(message):
    if message.from_user.id in admins:
        bot.send_message(message.chat.id,
                         f"Adminлар:\n{admins}")
    else:
        bot.send_message(message.chat.id, "Рухсат йўқ ❌")

# ====== BOT POLLING ======
bot.polling(none_stop=True)
