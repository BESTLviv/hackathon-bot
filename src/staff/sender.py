from enum import Enum
import re

from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telebot import TeleBot
from mongoengine.queryset.queryset import QuerySet

from ..data import Data
from ..data.user import User, Team


class DestinationEnum(Enum):
    ALL = "msg ALL"
    ALL_REGISTERED = "msg ALL_REGISTERED"
    ALL_UNREGISTERED = "msg ALL UNREGISTERED"
    ALL_WITH_TEAMS = "msg ALL WITH TEAMS"  # those who passed test task
    TEAM = "msg TEAM"
    USER = "msg USER"
    ME = "msg ME"

    @classmethod
    def common_destinations(cls):
        return [
            cls.ALL.value,
            cls.ALL_REGISTERED.value,
            cls.ALL_UNREGISTERED.value,
            cls.ALL_WITH_TEAMS.value,
            cls.ME.value,
        ]


class CustomMessage:
    text: str
    photo: str
    markup: InlineKeyboardMarkup

    def __init__(self):
        self.photo = None
        self.markup = InlineKeyboardMarkup()

    def format(self):
        self._extract_buttons()

    def send(self, bot: TeleBot, user: User):

        if self.photo:
            bot.send_photo(
                user.chat_id,
                photo=self.photo,
                caption=self.text,
                reply_markup=self.markup,
            )
        else:
            bot.send_message(user.chat_id, text=self.text, reply_markup=self.markup)

    def _extract_buttons(self):
        split_text = self.text.split("[btn]")

        self.text = split_text[0]
        buttons = split_text[1:]

        for btn in buttons:
            custom_btn = CustomButton()

            custom_btn.name = re.search(r"name=(.*?)]", btn).group(1)
            custom_btn.link = re.search(r"link=(.*?)]", btn).group(1)

            self.markup.add(custom_btn.form_btn())


class CustomButton:
    name: str
    link: str

    def form_btn(self) -> InlineKeyboardButton:
        return InlineKeyboardButton(text=self.name, url=self.link)


class Sender:
    custom_message: CustomMessage
    custom_message_input_rule = (
        "Надішли мені повідомлення текстом або текст+картинку\n\n"
        "Щоб вставити <i>кнопки-посилання</i> до повідомлення, то потрібно дотриматись наступного формату:\n"
        "\t\t*Основний текст*\n"
        "\t\t[btn][name=Кнопка1][link=https://google.com]\n"
        "\t\t[btn][name=Кнопка2][link=https://nestor.com]\n\n"
        "В результаті, ти отримаєш повідомлення з двома кнопками."
    )
    progress_text = "Користувачів оброблено {}/{}\nКориситувачів заблоковано {}"
    CANCEL_BUTTON_TEXT = "Скасувати"

    def __init__(
        self,
        data: Data,
        admin: User,
        destination: str,
        prev_admin_menu: "Callable" = None,
    ):
        self.data = data
        self.admin = admin
        self.prev_admin_menu = prev_admin_menu

        self.receiver_list: QuerySet = self._get_receiver_list(destination)

    def send_custom_message(self):
        bot = self.data.bot

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        cancel_btn = KeyboardButton(text=self.CANCEL_BUTTON_TEXT)
        markup.add(cancel_btn)

        bot.send_message(
            self.admin.chat_id,
            text=self.custom_message_input_rule,
            disable_web_page_preview=True,
            reply_markup=markup,
        )

        bot.register_next_step_handler_by_chat_id(
            self.admin.chat_id, self._process_input
        )

    def _process_input(self, message: Message):
        content_type = message.content_type
        self.custom_message = CustomMessage()

        if content_type == "text":
            if message.text == self.CANCEL_BUTTON_TEXT:
                self.data.bot.send_message(
                    self.admin.chat_id,
                    text="Скасовано!.",
                    reply_markup=ReplyKeyboardRemove(),
                )
                self._return_to_prev_admin_menu()
                return

            self.custom_message.text = message.text

        elif content_type == "photo":
            self.custom_message.text = message.caption
            self.custom_message.photo = message.photo

        else:
            self.data.bot.send_message(
                self.admin.chat_id, text="Підтримується лише розсилка тексту та фото."
            )
            return

        self._send_messages()

    def _send_messages(self):
        try:
            self.custom_message.format()
        except Exception as e:
            self.data.bot.send_message(self.admin.chat_id, text=f"{e}")
            return

        receivers_count = self.receiver_list.count()
        progress_message = self.data.bot.send_message(
            self.admin.chat_id,
            text=self.progress_text.format(0, receivers_count, 0),
        )

        blocked_users = 0
        for _id, user in enumerate(self.receiver_list, 1):
            try:
                self.custom_message.send(self.data.bot, user)
            except Exception as e:
                self.data.bot.send_message(self.admin.chat_id, text=f"{e}")
                blocked_users += 1

            if _id % 10 == 0:
                self.data.bot.edit_message_text(
                    text=self.progress_text.format(_id, receivers_count, blocked_users),
                    chat_id=self.admin.chat_id,
                    message_id=progress_message.message_id,
                )

        self.data.bot.edit_message_text(
            text=self.progress_text.format(
                receivers_count, receivers_count, blocked_users
            ),
            chat_id=self.admin.chat_id,
            message_id=progress_message.message_id,
            reply_markup=ReplyKeyboardRemove(),
        )

        self._return_to_prev_admin_menu()

    def _get_receiver_list(self, destination: str) -> QuerySet:

        if destination == DestinationEnum.ALL.value:
            return User.objects.filter(is_blocked=False)

        elif destination == DestinationEnum.ALL_WITH_TEAMS.value:
            return User.objects.filter(team__ne=None)

        elif destination == DestinationEnum.ALL_REGISTERED.value:
            return User.objects.filter(additional_info__ne=None)

        elif destination == DestinationEnum.ALL_UNREGISTERED.value:
            return User.objects.filter(additional_info=None)

        elif destination == DestinationEnum.TEAM.value:
            pass

        elif destination == DestinationEnum.USER.value:
            pass

        elif destination == DestinationEnum.ME.value:
            return User.objects.filter(chat_id=self.admin.chat_id)

    def _return_to_prev_admin_menu(self):
        if self.prev_admin_menu:
            self.prev_admin_menu(self.admin)