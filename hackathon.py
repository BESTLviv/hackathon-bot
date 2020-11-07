from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta


class Hackathon:

    STATUS_CREATED = 0
    STATUS_REGISTRATION_OPEN = 1
    STATUS_REGISTRATION_ENDED = 2
    STATUS_HACK_STARTED = 3
    STATUS_HACK_ENDED = 4

    # Tap 5 time on button to start/end event
    START_COUNTER = 0
    END_COUNTER = 0
    CLICKS_TO_ACTION = 5
    
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.bot = data.bot

        try:
            self.hackathon = self.data.get_hackathon().next()
        except:
            self.hackathon = None

        self.COMMAND_HACKATHON = KeyboardButton("Хакатон")
        self.COMMAND_SCHEDULE = KeyboardButton("Розклад")
        self.COMMAND_QUEST = KeyboardButton("Завдання")
        self.COMMAND_PARTNER_QUEST = KeyboardButton("Завдання від партнера")
        self.COMMAND_NEED_HELP = KeyboardButton("Потрібна допомога")
        self.COMMAND_TIME = KeyboardButton("Час")
        

    def start_event(self, call):
        if self.hackathon["status"] == self.STATUS_HACK_STARTED:
            self.bot.answer_callback_query(call.id, text=f"Хакатон вже триває")
            return

        self.START_COUNTER += 1
        if self.START_COUNTER != self.CLICKS_TO_ACTION:
            clicks_left = self.CLICKS_TO_ACTION - self.START_COUNTER
            self.bot.answer_callback_query(call.id, text=f"Натискань залишилось - {clicks_left}")
            return

        
        self.data.update_hackathon(set_={"status":self.STATUS_HACK_STARTED, 
                                         "start_time":datetime.now(),
                                         "end_time":datetime.now()+timedelta(days=1)})
        self.update_hackathon()

        hack_start_text = "Хакатон розпочато!!!\nБажаємо всім успіхів!!!"
        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=hack_start_text)
        self.send_message_to_participants(text=hack_start_text)


    def end_event(self, call):
        if self.hackathon["status"] != self.STATUS_HACK_STARTED:
            self.bot.answer_callback_query(call.id, text=f"Хакатон ще навіть не почався!")
            return

        self.END_COUNTER += 1
        if self.END_COUNTER != self.CLICKS_TO_ACTION:
            clicks_left = self.CLICKS_TO_ACTION - self.END_COUNTER
            self.bot.answer_callback_query(call.id, text=f"Натискань залишилось - {clicks_left}")
            return


        self.data.update_hackathon(set_={"status":self.STATUS_HACK_ENDED})
        self.update_hackathon()

        hack_end_text = "Хакатон закінчено!!!"
        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=hack_end_text)
        self.send_message_to_participants(text=hack_end_text)


    def send_main_info(self, chat_id):
        is_user_registered = self.is_user_registered(chat_id)
        
        registered_info = str()
        if is_user_registered:
            team = self.get_user_team(chat_id)
            registered_info = f"<b>Твоя команда - {team['name']}</b>"
        
        text = (f"{self.hackathon['description']}\n\n"
                f"{registered_info}"
        )
        photo = self.hackathon["photo"]

        self.bot.send_photo(chat_id, caption=text, photo=photo, reply_markup=self.get_keyboard(chat_id), parse_mode="HTML")
        
        # Send registration form is user is not registered yet
        if self.hackathon["status"] < self.STATUS_HACK_STARTED and is_user_registered is False:
            register_text = "Нажимай на кнопку та заповнюй форму!"
            registration_url = self.hackathon["registration_form"]

            markup = InlineKeyboardMarkup()
            btn = InlineKeyboardButton(text="Натискай на мене!", url=registration_url)
            markup.add(btn)

            self.bot.send_message(chat_id, text=register_text, reply_markup=markup)

    def send_schedule_info(self, chat_id):
        photo = self.hackathon["schedule_photo"]

        self.bot.send_photo(chat_id, photo=photo, reply_markup=self.get_keyboard(chat_id))

    def send_task_info(self, chat_id):
        team = self.get_user_team(chat_id)
        team_task = team["task_photo"]

        self.bot.send_photo(chat_id, photo=team_task)

    def send_partner_task_info(self, chat_id):
        team = self.get_user_team(chat_id)
        team_partner_task = team["partner_task_photo"]

        self.bot.send_photo(chat_id, photo=team_partner_task)

    def send_need_help_info(self, chat_id):
        text_wait = "Зачекайте, зараз з вами зв'яжуться адміністратори!"

        self.bot.send_message(chat_id, text=text_wait)

        # send help request info to admins
        who = self.data.get_user(where={"chat_id":chat_id}).next()
        team = self.get_user_team(chat_id)
        members = self.get_team_member_usernames_list(team=team)

        text_to_admins = (f"<b>Потребує допомоги</b> - @{who['username']}\n\n"
                f"<b>Команда</b> - {team['name']}\n"
                f"<b>Учасники</b> - {members}")
        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=text_to_admins, parse_mode="HTML")

    def send_time_info(self, chat_id):
        
        hack_end_time = self.hackathon["end_time"]
        time_left = str(hack_end_time - datetime.now()).split(".")[0]

        text = f"Залишилось часу - <b>{time_left}</b>"

        self.bot.send_message(chat_id, text=text, parse_mode="HTML")


    def add_new_team(self):
        text_to_admin = ("Надішли мені назву і склад команди у наступному форматі:\n\n"
                         "Назва команди\n"
                         "@учасник_1\n"
                         "@учасник_2\n"
                         "@учасник_N")

        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=text_to_admin, parse_mode="HTML")
        self.bot.register_next_step_handler_by_chat_id(self.data.ADMIN_CHAT_ID, self.process_add_new_team)

    def process_add_new_team(self, message):
        def check_every_member_registration(team_members):
            team_users = list()
            for member in team_members:
                try:
                    user = self.data.get_user(where={"username":member[1:].strip()}).next()
                except:
                    return (member, False)

                # if user is alredy in a team
                if user["team_id"] is None:
                    team_users += [user]
                else:
                    return (member, False)
            return (team_users, True)

        if message.content_type == "text":
            if message.text[0] == "/":
                return

            splitted_msg = message.text.split("\n")
            try:
                team_name = splitted_msg[0]
                team_members = splitted_msg[1:]
                if len(team_members) == 0:
                    self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text="Неправильний формат", parse_mode="HTML")
                    self.add_new_team()
                    return
            except:
                self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text="Неправильний формат", parse_mode="HTML")
                self.add_new_team()
                return

            # Check if every participant of a team is registered in bot and nobody register in team
            # And get a list of them
            team_users, all_registered = check_every_member_registration(team_members)
            if  all_registered == False:
                self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, 
                                      text=f"{team_users.strip()} не зареєстрований у боті або він вже є учасником команди!", 
                                      parse_mode="HTML")
                self.add_new_team()
                return

            # Create team and connect every member to it
            # Send every member notification about team creation
            team_id = self.data.add_team(name=team_name)
            for member in team_users:
                try:
                    self.data.update_user(set_={"team_id":team_id}, where={"username":member["username"]})
                    notification_to_member = f"Вітаємо!\nВаша команда <b>{team_name}</b> зареєстрована у Хакатоні!"
                    self.bot.send_message(member["chat_id"], text=notification_to_member, parse_mode="HTML")
                except:
                    continue

        else:
            self.add_new_team()
            return

        self.update_hackathon()
        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=f"Вітаємо!\nКоманда <b>{team_name}</b> зареєстрована у Хакатоні!", parse_mode="HTML")


    def send_admin_message_to_participants(self):
        text_to_admin = "Надішли мені повідомлення і я надішлю його всім учасникам!"
        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=text_to_admin)

        self.bot.register_next_step_handler_by_chat_id(self.data.ADMIN_CHAT_ID, self.process_send_message_to_participants)

    def process_send_message_to_participants(self, message):
        text = None
        photo = None

        content_type = message.content_type
        if content_type == "text":
            text = message.text
        elif content_type == "photo":
            text = message.caption
            photo = message.photo[-1].file_id
        else:
            self.send_admin_message_to_participants()
            return

        self.send_message_to_participants(text, photo)


    def change_description(self):
        text_to_admin = "Надішли мені новий опис!"
        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=text_to_admin)

        self.bot.register_next_step_handler_by_chat_id(self.data.ADMIN_CHAT_ID, self.process_change_description)

    def process_change_description(self, message):

        if message.content_type == "text":
            text = message.text
            self.data.update_hackathon(set_={"description":text})
        else:
            self.change_description()
            return
        
        self.update_hackathon()
        self.bot.send_message(self.data.ADMIN_CHAT_ID, text="Опис успішно змінено!")
        

    def change_photo(self, main=False, schedule=False):
        text_to_admin = "Надішли мені фото!"
        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=text_to_admin)

        self.bot.register_next_step_handler_by_chat_id(self.data.ADMIN_CHAT_ID, self.process_change_photo,
                                                       main=main, schedule=schedule)

    def process_change_photo(self, message, **kwargs):
        main = kwargs["main"]
        schedule = kwargs["schedule"]

        if message.content_type == "photo":
            photo = message.photo[-1].file_id
            if main:
                self.data.update_hackathon(set_={"photo":photo})
            if schedule:
                self.data.update_hackathon(set_={"schedule":photo})
        else:
            self.change_photo(main, schedule)
            return
        

        if main:
            obj = "Головне фото"
        if schedule:
            obj = "Розклад"

        self.update_hackathon()
        self.bot.send_message(self.data.ADMIN_CHAT_ID, text=f"{obj} успішно змінено!")
     
    
    def change_task(self, team_name, main=False, partner=False):
        text_to_admin = "Надішли мені фото!"
        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=text_to_admin)

        self.bot.register_next_step_handler_by_chat_id(self.data.ADMIN_CHAT_ID, self.process_change_task,
                                                       team_name=team_name, main=main, partner=partner)

    def process_change_task(self, message, **kwargs):
        team_name = kwargs["team_name"]
        main = kwargs["main"]
        partner = kwargs["partner"]

        if message.content_type == "photo":
            photo = message.photo[-1].file_id
            if main:
                self.data.update_team(set_={"task_photo":photo}, where={"name":team_name})
            if partner:
                self.data.update_team(set_={"partner_task_photo":photo}, where={"name":team_name})
        else:
            self.change_photo(team_name, main, partner)
            return
        

        if main:
            obj = "Завдання"
        if partner:
            obj = "Завдання від партнера"

        self.update_hackathon()
        self.bot.send_message(self.data.ADMIN_CHAT_ID, text=f"{obj} успішно змінено!\n/start")


    def send_message_to_participants(self, text, photo=None):
        users = self.data.get_user()

        for user in users:
            if user["team_id"] is None:
                continue
            user_chat_id = user["chat_id"]
            try:
                markup = self.get_keyboard(user_chat_id)
                if photo is None:
                    self.bot.send_message(chat_id=user_chat_id, text=text, reply_markup=markup)
                else:
                    self.bot.send_photo(chat_id=user_chat_id, caption=text, photo=photo, reply_markup=markup)
            except:
                continue

    
    def is_running(self):
        hack = self.data.get_hackathon().next()

        if hack["status"] == self.STATUS_HACK_STARTED:
            return True
        else:
            return False

    def is_user_registered(self, chat_id):
        user = self.data.get_user(where={"chat_id":chat_id}).next()

        if user['team_id'] is not None:
            return True
        else:
            return False

    def get_keyboard(self, chat_id):
        hack_menu = ReplyKeyboardMarkup(resize_keyboard=True)
        hack_menu.add(self.COMMAND_HACKATHON, self.COMMAND_SCHEDULE)

        if self.is_running() and self.is_user_registered(chat_id):
            hack_menu.add(self.COMMAND_QUEST, self.COMMAND_PARTNER_QUEST)
            hack_menu.add(self.COMMAND_NEED_HELP, self.COMMAND_TIME)

        return hack_menu

    def get_user_team(self, chat_id):
        user = self.data.get_user(where={"chat_id":chat_id}).next()

        team_id = user["team_id"]
        team = self.data.get_team(where={"_id":team_id}).next()

        return team

    def get_team_member_usernames_list(self, team):
        team_id = team["_id"]

        team_members = self.data.get_user(where={"team_id":team_id})

        team_member_usernames = list()
        for member in team_members:
            team_member_usernames += [f"@{member['username']}"]

        return team_member_usernames

    def update_hackathon(self):
        self.hackathon = self.data.get_hackathon().next()

    def null_counters(self):
        self.START_COUNTER = 0
        self.END_COUNTER = 0