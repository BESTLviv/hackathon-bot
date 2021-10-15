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

    @property
    def admin_info(self) -> str:
        return "Привіт Адмін!"

    def process_callback(self, user: User, call: CallbackQuery):
        action = call.data.split(";")[1]

        if action == "AdminMenu":
            self.send_admin_menu(user, call)

        elif action == "MailMenu":
            self.send_mail_menu(user, call)

        elif action in self._mailing_destinations:
            self._process_mailing(user, call)

        elif action == "TeamListMenu":
            self.send_team_list_menu(user, call)

        elif action == "TeamInfoMenu":
            self.send_team_info_menu(user, call)

        self.bot.answer_callback_query(call.id)

    def send_admin_menu(self, user: User, call: CallbackQuery = None):
        text = self.admin_info
        markup = self._form_main_admin_markup()

        self._send_menu(user, text, photo=None, markup=markup, call=call)

    def send_mail_menu(self, user: User, call: CallbackQuery = None):
        text = "Вибирай кому повідомлення надсилати будемо"
        markup = self._form_mail_menu_markup()

        self._send_menu(user, text, photo=None, markup=markup, call=call)

    def send_team_list_menu(self, user: User, call: CallbackQuery = None):
        text = self.admin_info
        markup = self._form_team_list_menu_markup()

        self._send_menu(user, text, photo=None, markup=markup, call=call)

    def send_team_info_menu(self, user: User, call: CallbackQuery = None):
        team_name = call.data.split(";")[2]
        team = Team.objects.filter(name=team_name).first()

        text = team.full_info
        markup = self._form_team_info_menu_markup(team=team)

        self._send_menu(user, text, photo=None, markup=markup, call=call)

    def _send_menu(
        self,
        user: User,
        text: str,
        photo: str = None,
        markup: InlineKeyboardMarkup = None,
        call: CallbackQuery = None,
    ):
        if call:
            self.send_message(call, text=text, reply_markup=markup)
        else:
            self.bot.send_message(user.chat_id, text, reply_markup=markup)

    def _process_mailing(self, user: User, call: CallbackQuery):
        destination = call.data.split(";")[1]
        team_name = call.data.split(";")[2]

        prev_admin_menu = self.send_team_list_menu if team_name else self.send_mail_menu

        sender = Sender(
            data=self.data,
            admin=user,
            destination=destination,
            team_name=team_name,
            prev_admin_menu=prev_admin_menu,
        )
        sender.send_custom_message()

    def _form_main_admin_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()

        mail_menu_btn = InlineKeyboardButton(
            text="Розсилка",
            callback_data=self.form_admin_callback(action="MailMenu", edit=True),
        )
        markup.add(mail_menu_btn)

        team_list_menu_btn = InlineKeyboardButton(
            text="Список команд",
            callback_data=self.form_admin_callback(action="TeamListMenu", edit=True),
        )
        markup.add(team_list_menu_btn)

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

    def _form_team_list_menu_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()

        for team in Team.objects:
            btn = InlineKeyboardButton(
                text=f"{team.name} - {team.test_task_status[0]}",
                callback_data=self.form_admin_callback(
                    action="TeamInfoMenu", team_name=team.name, edit=True
                ),
            )
            markup.add(btn)

        back_btn = self.create_back_button(
            callback_data=self.form_admin_callback(action="AdminMenu", edit=True)
        )
        markup.add(back_btn)

        return markup

    def _form_team_info_menu_markup(self, team: Team) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()

        mail_team_btn = InlineKeyboardButton(
            text="Надіслати повідомлення",
            callback_data=self.form_admin_callback(
                action=DestinationEnum.TEAM.value, team_name=team.name, new=True
            ),
        )
        markup.add(mail_team_btn)

        back_btn = self.create_back_button(
            callback_data=self.form_admin_callback(
                action="TeamListMenu", team_name=team.name, edit=True
            )
        )
        markup.add(back_btn)

        return markup