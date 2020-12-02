from telebot import TeleBot


from data import Data

from admin import Admin
import hackathon
import system

API_TOKEN = ""

bot = TeleBot(API_TOKEN)
data = Data(bot=bot)

hack = hackathon.Hackathon(data=data)
admin = Admin(data=data, hackathon=hack)


@bot.message_handler(commands=['start'])
def start_bot(message):
    chat_id = message.chat.id

    # This can be deleted after first start of bot
    if hack.hackathon is None:
        data.add_hackathon(name="Hackathon 2020")
        hack.update_hackathon()

    if chat_id == data.ADMIN_CHAT_ID:
        admin.send_admin_menu()
    else:
        system.add_user(data, message)
        hack.send_main_info(chat_id)


@bot.message_handler(func=lambda message: message.text == hack.COMMAND_HACKATHON.text, content_types=['text'])
def hackathon_info(message):
    system.update_user_interaction_time(data, message)
    
    chat_id = message.chat.id
    try:
        hack.send_main_info(chat_id)
    except:
        pass


@bot.message_handler(func=lambda message: message.text == hack.COMMAND_SCHEDULE.text, content_types=['text'])
def schedule_info(message):
    system.update_user_interaction_time(data, message)
    
    chat_id = message.chat.id
    try:
        hack.send_schedule_info(chat_id)
    except:
        pass


@bot.message_handler(func=lambda message: message.text == hack.COMMAND_QUEST.text, content_types=['text'])
def task_info(message):
    system.update_user_interaction_time(data, message)
    
    chat_id = message.chat.id
    try:
        hack.send_task_info(chat_id)
    except:
        pass

@bot.message_handler(func=lambda message: message.text == hack.COMMAND_PARTNER_QUEST.text, content_types=['text'])
def partner_task_info(message):
    system.update_user_interaction_time(data, message)
    
    chat_id = message.chat.id
    try:
        hack.send_partner_task_info(chat_id)
    except:
        pass


@bot.message_handler(func=lambda message: message.text == hack.COMMAND_NEED_HELP.text, content_types=['text'])
def help_request(message):
    system.update_user_interaction_time(data, message)
    
    chat_id = message.chat.id
    try:
        hack.send_need_help_info(chat_id)
    except:
        pass


@bot.message_handler(func=lambda message: message.text == hack.COMMAND_TIME.text, content_types=['text'])
def time_request(message):
    system.update_user_interaction_time(data, message)
    
    chat_id = message.chat.id
    try:
        hack.send_time_info(chat_id)
    except:
        pass


@bot.message_handler(func=lambda message: message.text == data.DESTROY_PASSWORD, content_types=['text'])
def destroy_all_data(message):
    data.destroy_all()
    bot.send_message(message.chat.id, text="Всі дані знищені")
    #data.add_hackathon(name="Hackathon 2020")
    #hack.update_hackathon()

@bot.callback_query_handler(func=lambda call: "Admin" in call.data.split(";")[0])
def handle_admin_query(call):
    
    try:
        admin.process_callback(call)
    except:
        oops(call)


def oops(call):
    oops_text = "Щось пішло не так :("
    bot.answer_callback_query(call.id, text=oops_text)

if __name__ == "__main__":
    bot.polling(none_stop=True)