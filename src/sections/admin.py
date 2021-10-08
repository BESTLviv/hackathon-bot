from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from ..data import Data
from ..data.user import User, Team
from .section import Section
from ..staff.sender import Sender, DestinationEnum


class AdminSection(Section):

    MENU_PHOTO: str = ""

    def __init__(self, data: Data):
        super().__init__(data)
        self._mailing_destinations = [v.value for v in DestinationEnum]

    def process_callback(self, user: User, call: CallbackQuery):
        action = call.data.split(";")[1]

        if action == "AdminMenu":
            self.send_admin_menu(user, call)

        elif action == "MailMenu":
            self.send_mail_menu(user, call)

        elif action in self._mailing_destinations:
            self.process_mailing(user, call)

        self.bot.answer_callback_query(call.id)

    def send_admin_menu(self, user: User, call: CallbackQuery = None):
        text = "Привіт Адмін!"
        markup = self._form_main_admin_markup()

        if call:
            self.send_message(call, text=text, reply_markup=markup)
        else:
            self.bot.send_message(user.chat_id, text, reply_markup=markup)

    def send_mail_menu(self, user: User, call: CallbackQuery = None):
        text = "Вибирай кому повідомлення надсилати будемо"
        markup = self._form_mail_menu_markup()

        if call:
            self.send_message(call, text=text, reply_markup=markup)
        else:
            self.bot.send_message(user.chat_id, text, reply_markup=markup)

    def process_mailing(self, user: User, call: CallbackQuery):
        destination = call.data.split(";")[1]

        sender = Sender(
            data=self.data,
            admin=user,
            destination=destination,
            prev_admin_menu=self.send_mail_menu,
        )
        sender.send_custom_message()

    def _form_main_admin_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()

        mail_menu_btn = InlineKeyboardButton(
            text="Розсилка",
            callback_data=self.form_admin_callback(action="MailMenu", edit=True),
        )

        markup.add(mail_menu_btn)

        return markup

    def _form_mail_menu_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()

        for dest in DestinationEnum.common_destinations():
            btn = InlineKeyboardButton(
                text=dest, callback_data=self.form_admin_callback(action=dest, new=True)
            )

            markup.add(btn)

        back_btn = self.create_back_button(
            callback_data=self.form_admin_callback(action="AdminMenu", edit=True)
        )
        markup.add(back_btn)

        return markup