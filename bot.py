from telebot import TeleBot

from data import Data

from sections.main import Main
from sections.hack import Hack

API_TOKEN = "1279034718:AAF8PJyO9YWcW06ug-Gs8QIHKJyHd8iIfDc"

bot = TeleBot(API_TOKEN)
data = Data(bot=bot)

main_menu = Main(data=data)
hack_menu = Hack(data=data)

@bot.message_handler(commands=['start'])
def start_bot(message):
    main_menu.send_start_message(chat_id=message.chat.id)    

@bot.callback_query_handler(func=lambda call: "Main" in call.data.split(";")[0])
def handle_main_menu_query(call):

    try:
        main_menu.process_callback(call)
    except:
        oops(call)

@bot.callback_query_handler(func=lambda call: "Hack" in call.data.split(";")[0])
def handle_main_menu_query(call):

    try:
        hack_menu.process_callback(call)
    except:
        oops(call)

@bot.callback_query_handler(func=lambda call: True)
def handle_etc_query(call):
    
    if call.data == "DELETE":
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except:
            bot.answer_callback_query(call.id, text=data.message.delete_error)
    elif call.data == "IGNORE":
        bot.answer_callback_query(call.id)
    else:
        oops(call)

def oops(call):
    oops_text = data.message.oops
    bot.answer_callback_query(call.id, text=oops_text)

if __name__ == "__main__":
    bot.polling()