from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from ..data import Data
from ..data.user import User, Team
from .section import Section
from ..staff.sender import Sender, DestinationEnum


class AdminSection(Section):

    MENU_PHOTO: str = ""
    TEAM_LIST_SIZE: int = 10
    TEAM_DELETION_CONFIRMATION: str = "DELETE"

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

        elif action.split(":")[0] == "TeamListMenu":
            self.send_team_list_menu(user, call)

        elif action.split(":")[0] == "ReviewTask":
            team_id = call.data.split(";")[2]
            is_approved = bool(int(action.split(":")[1]))
            self.review_task(user, call, team_id, is_approved)

        elif action == "TeamInfoMenu":
            self.send_team_info_menu(user, call)

        elif action == "DeleteTeam":
            team_id = call.data.split(";")[2]
            self.delete_team(user, team_id, call=call)

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
        text = f"Кількість команд - {Team.objects.count()}"
        try:
            page_number = int(call.data.split(";")[1].split(":")[1])
        except:
            page_number = 1

        markup = self._form_team_list_menu_markup(page_number)

        self._send_menu(user, text, photo=None, markup=markup, call=call)

    def send_team_info_menu(self, user: User, call: CallbackQuery = None):
        team_id = call.data.split(";")[2]
        team = Team.objects.get(id=team_id)

        text = team.full_info
        markup = self._form_team_info_menu_markup(team=team)

        self._send_menu(user, text, photo=None, markup=markup, call=call)

    def delete_team(
        self, user: User, team_id: str, confirmed=False, call: CallbackQuery = None
    ):
        def confirm_deletion(message: Message):

            if message.content_type == "text":
                if message.text == self.TEAM_DELETION_CONFIRMATION:
                    self.delete_team(user, team_id, confirmed=True)

                elif message.text == "Скасувати":
                    self.bot.send_message(user.chat_id, text="Скасовано!")
                    return

            else:
                self.delete_team(user, team_id, confirmed=False)
                return

        try:
            team = Team.objects.get(id=team_id)
        except:
            self.send_message(call, text="Ця команда вже була видалена")
            return

        if confirmed:
            team_name = team.name

            for member in team.members:
                member.leave_team()
            team.delete()
            team.save()

            self.bot.send_message(
                user.chat_id,
                text=f"Команда {team_name} успішно видалена!",
                reply_markup=ReplyKeyboardRemove(),
            )
            self.send_team_list_menu(user)

        else:
            markup = ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(KeyboardButton(text="Скасувати"))
            self.bot.send_message(
                user.chat_id,
                text=f"Для видалення команди {team.name} напиши слово-підтвeрдження -- {self.TEAM_DELETION_CONFIRMATION}",
                reply_markup=markup,
            )
            self.bot.register_next_step_handler_by_chat_id(
                user.chat_id, confirm_deletion
            )

    def review_task(
        self, user: User, call: CallbackQuery, team_id: str, is_approved: bool
    ):
        team: Team = Team.objects.get(id=team_id)
        admin_text = str()
        team_text = str()

        if is_approved:
            team.test_task_passed = True
            admin_text = f"Команда {team.name} бере участь в хакатоні!"
            team_text = (
                "Йоу йоу йоу!!!!\n"
                "Спішу повідомити вас, що ви пройшли на Хакатон🥳🥳 Для нас - це настільки ж прекрасна новина як і для вас, тому що - це чудо, мати таких крутих учасників в нашому проекті💚\n"
                "Сподіваємось, ви зарядилися цією інформацію і готові розривати всіх своїми навичками, а також ділитись енергією і так само мотивувати її показати найкращий результат😜\n"
                "Готуйтесь, але не забувайте work hard, play harder і тоді з вами цей хакатон стане легендарним, а разом з ним і його учасники🤗\n"
            )
        else:
            team.test_task_passed = False
            admin_text = f"Команда {team.name} не братиме участь в хакатоні!"
            team_text = (
                "Привіт-привіт!\n"
                "Ми розглянули вашу подачу на Хакатон. Ви великі молодці, що виконали тестове завдання і це вже дуже круто!😎👍Вам не вистачило зовсім трішки аби стати учасниками.\n"
                "Проте, не сумуйте та не опускайте руки, ми чекатимемо вас на наступних наших проектах!\n"
                "Команда [BEST::Hackath0n'6]💚)\n"
            )

        team.save()

        receivers_count = 0
        for member in team.members:
            self.bot.send_message(member.chat_id, text=team_text)
            receivers_count += 1

        self.bot.send_message(
            user.chat_id,
            text=f"{admin_text}\n\nНадіслано {receivers_count}/{team.members_count} повідомлень.",
        )

        self.send_team_info_menu(user, call)

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
        team_id = call.data.split(";")[2]

        prev_admin_menu = self.send_team_list_menu if team_id else self.send_mail_menu

        sender = Sender(
            data=self.data,
            admin=user,
            destination=destination,
            team_id=team_id,
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
            callback_data=self.form_admin_callback(action="TeamListMenu:1", edit=True),
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

    def _form_team_list_menu_markup(self, page_number: int) -> InlineKeyboardMarkup:
        def get_team_chunk(page_number):
            team_count = Team.objects.count()
            last_page_number = int(team_count / self.TEAM_LIST_SIZE) + 1

            # define correct page number
            if page_number == 0:
                page_number = last_page_number

            if page_number == last_page_number + 1:
                page_number = 1

            start_index = (page_number - 1) * self.TEAM_LIST_SIZE
            end_index = page_number * self.TEAM_LIST_SIZE

            if end_index > team_count:
                end_index = team_count

            return ([team for team in Team.objects[start_index:end_index]], page_number)

        markup = InlineKeyboardMarkup()

        teams, page_number = get_team_chunk(page_number)

        for team in teams:
            btn = InlineKeyboardButton(
                text=f"{team.name} - {team.test_task_status[0]} | {team.members_count}",
                callback_data=self.form_admin_callback(
                    action="TeamInfoMenu", team_id=team.id, edit=True
                ),
            )
            markup.add(btn)

        left_btn = InlineKeyboardButton(
            text="👈",
            callback_data=self.form_admin_callback(
                action=f"TeamListMenu:{page_number-1}", edit=True
            ),
        )
        counter_btn = InlineKeyboardButton(
            text=f"{page_number}/{int(Team.objects.count() / self.TEAM_LIST_SIZE) + 1}",
            callback_data="IGNORE",
        )
        right_btn = InlineKeyboardButton(
            text="👉",
            callback_data=self.form_admin_callback(
                action=f"TeamListMenu:{page_number+1}", edit=True
            ),
        )

        markup.add(left_btn, counter_btn, right_btn)

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
                action=DestinationEnum.TEAM.value, team_id=team.id, new=True
            ),
        )
        markup.add(mail_team_btn)

        if team.test_task and team.test_task_passed is None:
            approve_btn = InlineKeyboardButton(
                text="Approve",
                callback_data=self.form_admin_callback(
                    action="ReviewTask:1", team_id=team.id, edit=True
                ),
            )
            reject_btn = InlineKeyboardButton(
                text="Reject",
                callback_data=self.form_admin_callback(
                    action="ReviewTask:0", team_id=team.id, edit=True
                ),
            )
            markup.add(approve_btn, reject_btn)

        delete_team_btn = InlineKeyboardButton(
            text="Видалити команду",
            callback_data=self.form_admin_callback(
                action="DeleteTeam", team_id=team.id, delete=True
            ),
        )
        markup.add(delete_team_btn)

        back_btn = self.create_back_button(
            callback_data=self.form_admin_callback(
                action="TeamListMenu:1", team_id=team.id, edit=True
            )
        )
        markup.add(back_btn)

        return markup
