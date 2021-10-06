from datetime import date

from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from ..data import User, Data, Hackathon
from ..data.hackathon import ReplyButton
from ..sections.section import Section
from ..staff.quiz import start_starting_quiz


class MainMenuSection(Section):
    def __init__(self, data: Data):
        super().__init__(data)

    @property
    def special_buttons(self):
        return {
            "time_till_start": self._b_registration_start,
        }

    def send_start_menu(self, user: User):

        if user.is_registered is False:
            self._register_user(user)
            return

        self.data.hackathon.current_menu.send_menu(self.bot, user)

    def process_button(self, user: User, btn_name: str):

        button = self.data.hackathon.current_menu.get_btn_by_name(btn_name)

        if button.special_action is None:
            button.send_content(self.bot, user)

        else:
            self.special_buttons[button.special_action](user, button)

    def _register_user(self, user: User):
        self.bot.send_photo(
            user.chat_id,
            photo=self.data.hackathon.start_photo,
            caption=self.data.hackathon.start_text,
        )

        start_starting_quiz(user=user, bot=self.bot, final_func=self.send_start_menu)

    #################
    ## Informative
    #################

    def _b_registration_start(self, user: User, button: ReplyButton):
        self.bot.send_message(
            chat_id=user.chat_id,
            text=button.text.format(
                date=self.data.hackathon.p_registration_menu.start_date
            ),
        )

    #################
    ## Registration
    #################
