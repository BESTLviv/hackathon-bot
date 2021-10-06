import configparser
import os

from src.data import Data, User
from src.sections.admin import AdminSection

from src.sections.main_menu import MainMenuSection
from src.sections.team_menu import TeamMenu

from src.staff.updates import Updater

# from src.staff import utils

# from src.objects import quiz

from telebot import TeleBot, logger

config = configparser.ConfigParser()
config.read("Settings.ini")

API_TOKEN = (
    os.environ.get("TOKEN", False)
    if os.environ.get("TOKEN", False)
    else config["TG"]["token"]
)
CONNECTION_STRING = (
    os.environ.get("DB", False)
    if os.environ.get("DB", False)
    else config["Mongo"]["db"]
)

bot = TeleBot(API_TOKEN, parse_mode="HTML")
data = Data(conn_string=CONNECTION_STRING, bot=bot)

main_menu_section = MainMenuSection(data=data)
team_section = TeamMenu(data=data)
# admin_section = AdminSection(data=data)

updater = Updater(data=data)


@bot.message_handler(commands=["start"])
def start_bot(message):
    user = updater.update_user_interaction_time(message)

    try:
        main_menu_section.send_start_menu(user)
        return

        if user.additional_info is None:
            send_welcome_message_and_start_quiz(user)
        else:
            main_menu_section.send_start_menu(user)

    except Exception as e:
        print(f"Exception during start - {e}")


@bot.message_handler(content_types=["text"])
def handle_text_buttons(message):
    user = updater.update_user_interaction_time(message)
    message_text = message.text

    try:

        import time

        start = time.time()

        if message_text in data.hackathon.current_menu.buttons_list:
            if (
                data.hackathon.current_menu.get_btn_by_name(message_text).special_action
                == "team_info"
            ):
                team_section.send_team_info_menu(user)
            else:
                main_menu_section.process_button(user, message_text)

        elif message_text == "__next_menu":
            data.hackathon.switch_to_next_menu()
            main_menu_section.send_start_menu(user)

        bot.send_message(user.chat_id, f"{time.time() - start}")

    except Exception as e:
        print(e)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user = updater.update_user_interaction_time(call.message)
    section = call.data.split(";")[0]

    try:
        if section == "Team":
            team_section.process_callback(user, call)

    except Exception as e:
        print(e)


def send_welcome_message_and_start_quiz(user: User):
    hack = data.get_hackathon()
    welcome_text = hack.content.start_text
    welcome_photo = hack.content.start_photo
    bot.send_photo(user.chat_id, photo=welcome_photo, caption=welcome_text)

    final_func = hack_section.send_start_menu

    quiz.start_starting_quiz(user, bot, final_func)


if __name__ == "__main__":
    updater.start_update_threads()

    bot.polling(none_stop=True)
