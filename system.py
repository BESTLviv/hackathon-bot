from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime

def add_user(data, message):
    username = message.chat.username if message.chat.username is not None else "Безіменний"
    name = message.chat.first_name if message.chat.first_name is not None else "Безіменний"
    surname = message.chat.last_name if message.chat.last_name is not None else "0"
    chat_id = message.chat.id

    try:
        client_registered = data.get_user(where={"chat_id":chat_id}).count() >= 1
    except:
        print("Щось пішло не так")
        return

    if not client_registered:
        data.add_user(name, surname, username, chat_id)
    else:
        update_user_interaction_time(data, message)

def update_user_interaction_time(data, message):
    date = datetime.now()
    user_chat_id = message.chat.id

    try:
        user = data.get_user(where={"chat_id":user_chat_id}).next()
        click_count = int(user["click_count"]) + 1
        data.update_user(set_={"last_interaction_time":date, "click_count":click_count}, 
                         where={"chat_id":user_chat_id})
    except:
        add_user(data, message)