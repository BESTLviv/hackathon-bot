from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta


class Hackathon:

    STATUS_CREATED = 0
    STATUS_REGISTRATION_OPEN = 1
    STATUS_REGISTRATION_ENDED = 2
    STATUS_HACK_STARTED = 3
    STATUS_HACK_ENDED = 4

    # Tap 6 time on button to start/end event/delete team
    START_COUNTER = 0
    END_COUNTER = 0
    DELETE_TEAM_COUNTER = 0
    CLICKS_TO_ACTION = 6

    # Number of partners in one row of Keyboard in Partners menu
    KEYBOARD_PARTNERS_IN_ROW = 2
    
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
        #self.COMMAND_PARTNER_QUEST = KeyboardButton("Завдання від партнера")
        self.COMMAND_NEED_HELP = KeyboardButton("Потрібна допомога")
        self.COMMAND_TIME = KeyboardButton("Час")
        self.COMMAND_MENTORS = KeyboardButton("Менторство")
        self.COMMAND_PARTNERS = KeyboardButton("Партнери")
        self.COMMAND_BACK = KeyboardButton("🔙Назад")

        self.COMMAND_PARTNERS_LIST = list()
        self.COMMAND_PARTNERS_KEYBOARD = ReplyKeyboardMarkup(resize_keyboard=True)
        self.update_partners()
        

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

        hack_start_text = ("Увага: BEST::HACKath0n починається прямо зараз! Наступні 24 години будуть "
                           "присвячені розробці вашого проекту. Всю детальну інформацію знайдете в боті." 
                           "У секції “Завдання” ви побачите підтему, яка була вибрана для кожної команди з допомогою рандомайзера." 
                           "Бажаємо всім удачі! Hack with us.")
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

        hack_end_text = ("Увага: BEST::HACKath0n завершено! Дякуємо командам "
                         "за ці 24 години кодингу та крутої атмосфери. Скоро "
                         "презентації команд, тож готуйтеся. Зустрінемось вже дуже скоро :)"
        )
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
        #if self.hackathon["status"] < self.STATUS_HACK_STARTED and is_user_registered is False:
        #    register_text = "Нажимай на кнопку та заповнюй форму!"
        #    registration_url = self.hackathon["registration_form"]
        #
        #    markup = InlineKeyboardMarkup()
        #    btn = InlineKeyboardButton(text="Натискай на мене!", url=registration_url)
        #    markup.add(btn)
        #
        #    self.bot.send_message(chat_id, text=register_text, reply_markup=markup)

    def send_schedule_info(self, chat_id):
        photo = self.hackathon["schedule_photo"]

        self.bot.send_photo(chat_id, photo=photo, reply_markup=self.get_keyboard(chat_id))

    def send_task_info(self, chat_id):
        team = self.get_user_team(chat_id)
        team_task = team["task_photo"]
        team_task_text = team["task_text"]

        self.bot.send_photo(chat_id, photo=team_task, caption=team_task_text, parse_mode="HTML")

    def send_partner_task_info(self, chat_id):
        team = self.get_user_team(chat_id)
        team_partner_task = team["partner_task_photo"]
        team_partner_task_text = team["partner_task_text"]
        team_partner_task_link = team["partner_task_link"]

        link_text = "Натисни на мене"
        markup = InlineKeyboardMarkup()
        btn = InlineKeyboardButton(text=link_text, url=team_partner_task_link)
        markup.add(btn)

        try:
            self.bot.send_photo(chat_id, photo=team_partner_task, caption=team_partner_task_text, 
                                reply_markup=markup, parse_mode="HTML")
        except:
            self.bot.send_photo(chat_id, photo=team_partner_task, caption=team_partner_task_text, 
                                parse_mode="HTML")

    def send_need_help_info(self, chat_id):
        #text_wait = "Зачекайте, зараз з вами зв'яжуться адміністратори!"
        photo_wait = self.hackathon["need_help_photo"]

        self.bot.send_photo(chat_id, photo=photo_wait)

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
        photo = self.hackathon["time_photo"]

        self.bot.send_photo(chat_id, caption=text, photo=photo, parse_mode="HTML")

    def send_mentors_info(self, chat_id):
        mentors_text = self.hackathon["mentors_text"]
        mentors_photo = self.hackathon["mentors_photo"]

        if mentors_photo is None:
            mentors_photo = self.data.TEST_PHOTO

        self.bot.send_photo(chat_id, caption=mentors_text, photo=mentors_photo, parse_mode="HTML")

    def send_partner_info(self, chat_id, partner_name):
        """
        Send info about partner. Also get statistic
        for clicks on every partner.
        """
        # get partner info
        partner = self.data.get_partner(where={"name":partner_name})[0]
        partner_photo = partner["photo"]
        partner_description = partner["description"]
        partner_clicks_count = partner["clicks_count"]

        # update partner clicks
        self.data.update_partner(set_={"clicks_count":partner_clicks_count+1}, where={"name":partner_name})

        # send info about partner
        self.bot.send_photo(chat_id=chat_id, photo=partner_photo)
        self.bot.send_message(chat_id=chat_id, text=partner_description, 
                              parse_mode="HTML")


    def send_partner_menu(self, chat_id):
        partner_menu = self.get_partners_keyboard()

        partners_photo = self.hackathon["partners_photo"]
        partners_text = self.hackathon["partners_text"]

        self.bot.send_photo(chat_id=chat_id, photo=partners_photo, caption=partners_text,
                            reply_markup=partner_menu, parse_mode="HTML")


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

    def delete_team(self, call, team_name):
        self.DELETE_TEAM_COUNTER += 1
        if self.DELETE_TEAM_COUNTER != self.CLICKS_TO_ACTION:
            clicks_left = self.CLICKS_TO_ACTION - self.DELETE_TEAM_COUNTER
            self.bot.answer_callback_query(call.id, text=f"Натискань залишилось - {clicks_left}")
            return

        # delete team_id in every team member
        team= self.data.get_team(where={"name":team_name}).next()
        team_members_usernames_list = self.get_team_member_usernames_list(team=team)
        for username in team_members_usernames_list:
            self.data.update_user(set_={"team_id":None}, where={"username":username})
        # delete team
        self.data.delete_team(where={"name":team_name})

        self.bot.delete_message(chat_id=self.data.ADMIN_CHAT_ID, message_id=call.message.message_id)
        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=f"Команду {team_name} видалено!\n/start")

    def add_new_partner(self):
        text_to_admin = "Надішли мені фото партнера"

        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=text_to_admin, parse_mode="HTML")
        self.bot.register_next_step_handler_by_chat_id(self.data.ADMIN_CHAT_ID, self.process_add_new_partner,
                                                       step=1, photo=None, description=None)

    def process_add_new_partner(self, message, **kwargs):
        step = kwargs["step"]
        photo = kwargs["photo"]
        description = kwargs["description"]

        # step with photo
        if step == 1:
            if message.content_type == "photo":
                photo = message.photo[-1].file_id
                step = 2

                text_to_admin = "Надішли мені опис партнера!\nВ першому рядку опису повинна бути <b>назва</b> партнера"
                self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=text_to_admin, parse_mode="HTML")
                self.bot.register_next_step_handler_by_chat_id(self.data.ADMIN_CHAT_ID, self.process_add_new_partner,
                                                               step=step, photo=photo, description=description)
                return
            else:
                self.add_new_partner()
                return
        
        # step with text
        if step == 2:
            if message.content_type == "text":
                text = message.text
                name = text.split("\n")[0].strip()
                description = text[text.rfind('\n'):]
            else:
                self.add_new_partner()
                return
        

        self.data.add_partner(name, photo, text)
        self.update_partners()
        self.bot.send_message(self.data.ADMIN_CHAT_ID, text=f"Партнера {name} добавлено!\n/start")

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
        

    def change_mentors_section(self):
        text_to_admin = "Надішли мені фото + текст"
        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=text_to_admin)

        self.bot.register_next_step_handler_by_chat_id(self.data.ADMIN_CHAT_ID, self.process_change_mentors_section)

    def process_change_mentors_section(self, message):
        if message.content_type == "photo":
            photo = message.photo[-1].file_id
            text = message.caption
            self.data.update_hackathon(set_={"mentors_text":text, "mentors_photo":photo})
        else:
            self.change_mentors_section()
            return
        
        self.update_hackathon()
        self.bot.send_message(self.data.ADMIN_CHAT_ID, text="Секцію менторства успішно змінено!\n/start")
        self.send_mentors_info(chat_id=self.data.ADMIN_CHAT_ID)


    def change_partners_menu_section(self):
        text_to_admin = "Надішли мені фото + текст"
        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=text_to_admin)

        self.bot.register_next_step_handler_by_chat_id(self.data.ADMIN_CHAT_ID, self.process_change_partners_menu_section)

    def process_change_partners_menu_section(self, message):
        if message.content_type == "photo":
            photo = message.photo[-1].file_id
            text = message.caption
            self.data.update_hackathon(set_={"partners_text":text, "partners_photo":photo})
        else:
            self.change_partners_menu_section()
            return
        
        self.update_hackathon()
        self.bot.send_message(self.data.ADMIN_CHAT_ID, text="Секцію меню партнерів успішно змінено!\n/start")


    def change_photo(self, main=False, schedule=False, time=False, need_help=False):
        text_to_admin = "Надішли мені фото!"
        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=text_to_admin)

        self.bot.register_next_step_handler_by_chat_id(self.data.ADMIN_CHAT_ID, self.process_change_photo,
                                                       main=main, schedule=schedule, time=time, need_help=need_help)

    def process_change_photo(self, message, **kwargs):
        main = kwargs["main"]
        schedule = kwargs["schedule"]
        time = kwargs["time"]
        need_help = kwargs["need_help"]

        if message.content_type == "photo":
            photo = message.photo[-1].file_id
            if main:
                self.data.update_hackathon(set_={"photo":photo})
            if schedule:
                self.data.update_hackathon(set_={"schedule_photo":photo})
            if time:
                self.data.update_hackathon(set_={"time_photo":photo})
            if need_help:
                self.data.update_hackathon(set_={"need_help_photo":photo})
        else:
            self.change_photo(main, schedule, time, need_help)
            return
        

        if main:
            obj = "Головне фото"
        if schedule:
            obj = "Розклад"
        if time:
            obj = "Фото часу"
        if need_help:
            obj = "Фото запиту на допомогу"

        self.update_hackathon()
        self.bot.send_message(self.data.ADMIN_CHAT_ID, text=f"{obj} успішно змінено!")
     
    
    def change_task(self, team_name, main=False, partner=False):
        if main:
            text_to_admin = "Надішли мені фото з описом!"
        if partner:
            text_to_admin = "Надішли мені фото з описом!\nВ останньому рядку опису вкажіть ПОСИЛАННЯ"
        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=text_to_admin)

        self.bot.register_next_step_handler_by_chat_id(self.data.ADMIN_CHAT_ID, self.process_change_task,
                                                       team_name=team_name, main=main, partner=partner)

    def process_change_task(self, message, **kwargs):
        team_name = kwargs["team_name"]
        main = kwargs["main"]
        partner = kwargs["partner"]

        if message.content_type == "photo":
            photo = message.photo[-1].file_id
            description = message.caption
            if main:
                self.data.update_team(set_={"task_photo":photo, "task_text":description}, where={"name":team_name})
            if partner:
                link = description.split('\n')[-1].strip()
                description = description[:description.rfind('\n')]
                self.data.update_team(set_={"partner_task_photo":photo, "partner_task_text":description,
                                            "partner_task_link":link}, where={"name":team_name})
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
                    self.bot.send_message(chat_id=user_chat_id, text=text, reply_markup=markup, parse_mode="HTML")
                else:
                    self.bot.send_photo(chat_id=user_chat_id, caption=text, photo=photo, reply_markup=markup, parse_mode="HTML")
            except:
                continue
                
        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text="Успішно відправлено!")

    
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
            hack_menu.add(self.COMMAND_QUEST)
            hack_menu.add(self.COMMAND_TIME, self.COMMAND_NEED_HELP)
        
        hack_menu.add(self.COMMAND_PARTNERS, self.COMMAND_MENTORS)

        return hack_menu

    def get_partners_keyboard(self):
        return self.COMMAND_PARTNERS_KEYBOARD

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

    def update_partners(self):
        """
        Update partners list and keyboard
        Call this method after adding new parner into DB.
        """
        partners_list = self.data.get_partner()
        self.COMMAND_PARTNERS_LIST = list()
        self.COMMAND_PARTNERS_KEYBOARD = ReplyKeyboardMarkup(resize_keyboard=True)

        # form list and keyboard (n*2)
        keyboard_row = list()
        for partner in partners_list:
            partner_name = partner["name"]

            # list part
            self.COMMAND_PARTNERS_LIST += [partner_name]

            # keyboard part
            keyboard_row += [KeyboardButton(partner_name)]
            if len(keyboard_row) == self.KEYBOARD_PARTNERS_IN_ROW:
                self.COMMAND_PARTNERS_KEYBOARD.add(*keyboard_row)
                keyboard_row = list()
        
        # add the rest partners to keyboard
        if len(keyboard_row) < self.KEYBOARD_PARTNERS_IN_ROW:
            self.COMMAND_PARTNERS_KEYBOARD.add(*keyboard_row)
        # add "Головне меню" button to keyboard
        self.COMMAND_PARTNERS_KEYBOARD.add(self.COMMAND_BACK)



    def null_counters(self):
        self.START_COUNTER = 0
        self.END_COUNTER = 0
        self.DELETE_TEAM_COUNTER = 0
