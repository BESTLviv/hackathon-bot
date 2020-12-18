from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

class Admin:

    def __init__(self, data, hackathon):
        super().__init__()
        self.data = data
        self.bot = self.data.bot
        self.hackathon = hackathon

    def process_callback(self, call):
        action = call.data.split(";")[1]
        team_name = call.data.split(";")[2]
        chat_id = call.message.chat.id
        self.bot.clear_step_handler_by_chat_id(chat_id=chat_id)

        # null stop/start hack counters
        if (action != "StartHack" and action != "StopHack") and action != "DeleteTeam":
            self.hackathon.null_counters()


        if action == "Hack":
            self.send_admin_menu(call=call)

        elif action == "StartHack":
            self.hackathon.start_event(call)

        elif action == "StopHack":
            self.hackathon.end_event(call)

        elif action == "TeamList":
            self.send_team_list(call)

        elif action == "TeamDetail":
            self.send_team_detail(call, team_name)

        elif action == "AddTeam":
            self.hackathon.add_new_team()

        elif action == "SendMessageToAll":
            self.send_admin_message_to_all()

        elif action == "SendMessageToParticipants":
            self.hackathon.send_admin_message_to_participants()
        
        elif action == "SendMessageToTeam":
            self.send_admin_message_to_team(team_name)

        elif action == "SendTeamTasks":
            self.send_team_tasks(call, team_name)

        elif action == "ChangeHackPhoto":
            self.hackathon.change_photo(main=True)

        elif action == "ChangeHackSchedulePhoto":
            self.hackathon.change_photo(schedule=True)

        elif action == "ChangeHackDescription":
            self.hackathon.change_description()

        elif action == "ChangeTeamTask":
            self.hackathon.change_task(team_name, main=True)

        #elif action == "ChangeTeamPartnerTask":
        #    self.hackathon.change_task(team_name, partner=True)

        elif action == "ChangeTimeLeftPhoto":
            self.hackathon.change_photo(time=True)

        elif action == "ChangeMentorsSection":
            self.hackathon.change_mentors_section()

        elif action == "ChangeNeedHelpPhoto":
            self.hackathon.change_photo(need_help=True)

        elif action == "ChangePartnersMenuInfo":
            self.hackathon.change_partners_menu_section()

        elif action == "AddPartner":
            self.hackathon.add_new_partner()

        elif action == "DeleteTeam":
            self.hackathon.delete_team(call, team_name)

        else:
            pass

        self.bot.answer_callback_query(call.id)

    def send_admin_menu(self, call=None):

        admin_markup = InlineKeyboardMarkup()
        
        # Start Hack Button
        start_btn_text = "Розпочати хакатон"
        start_btn_callback = self.form_admin_callback(action="StartHack")
        start_btn = InlineKeyboardButton(start_btn_text, callback_data=start_btn_callback)
        # Stop Hack Button
        stop_btn_text = "Закінчити хакатон"
        stop_btn_callback = self.form_admin_callback(action="StopHack")
        stop_btn = InlineKeyboardButton(stop_btn_text, callback_data=stop_btn_callback)
        admin_markup.add(start_btn, stop_btn)


        # Team List Button
        team_list_btn_text = "Список команд"
        team_list_btn_callback = self.form_admin_callback(action="TeamList")
        team_list_btn = InlineKeyboardButton(team_list_btn_text, callback_data=team_list_btn_callback)
        # Add Team Button
        add_team_btn_text = "Добавити команду"
        add_team_btn_callback = self.form_admin_callback(action="AddTeam")
        add_team_btn = InlineKeyboardButton(add_team_btn_text, callback_data=add_team_btn_callback)
        admin_markup.add(team_list_btn, add_team_btn)


        # Send message to all Button
        send_msg_to_all_btn_text = "Зробити розсилку всім користувачам"
        send_msg_to_all_btn_callback = self.form_admin_callback(action="SendMessageToAll")
        send_msg_to_all_btn = InlineKeyboardButton(send_msg_to_all_btn_text, callback_data=send_msg_to_all_btn_callback)
        admin_markup.add(send_msg_to_all_btn)
        

        # Send message to all in game Button
        send_msg_to_game_btn_text = "Зробити розсилку всім УЧАСНИКАМ"
        send_msg_to_game_btn_callback = self.form_admin_callback(action="SendMessageToParticipants")
        send_msg_to_game_btn = InlineKeyboardButton(send_msg_to_game_btn_text, 
                                                    callback_data=send_msg_to_game_btn_callback)
        
        admin_markup.add(send_msg_to_game_btn)

        # CHANGES
        # Change hack photo
        change_btn_text = "Змінити фото"
        change_btn_callback = self.form_admin_callback(action="ChangeHackPhoto")
        photo_change_btn = InlineKeyboardButton(change_btn_text, callback_data=change_btn_callback)
        # Change hack schedule photo
        change_btn_text = "Змінити розклад"
        change_btn_callback = self.form_admin_callback(action="ChangeHackSchedulePhoto")
        schedule_photo_change_btn = InlineKeyboardButton(change_btn_text, callback_data=change_btn_callback)
        # Change hack description
        change_btn_text = "Змінити опис"
        change_btn_callback = self.form_admin_callback(action="ChangeHackDescription")
        description_change_btn = InlineKeyboardButton(change_btn_text, callback_data=change_btn_callback)
        admin_markup.add(photo_change_btn, schedule_photo_change_btn, description_change_btn)

        # Change hack time photo
        change_btn_text = "Змінити фото для часу"
        change_btn_callback = self.form_admin_callback(action="ChangeTimeLeftPhoto")
        time_left_photo_change_btn = InlineKeyboardButton(change_btn_text, callback_data=change_btn_callback)
        admin_markup.add(time_left_photo_change_btn)

        # Change mentors
        change_btn_text = "Змінити секцію менторства"
        change_btn_callback = self.form_admin_callback(action="ChangeMentorsSection")
        mentor_section_change_btn = InlineKeyboardButton(change_btn_text, callback_data=change_btn_callback)
        admin_markup.add(mentor_section_change_btn)

        # Change need_help and partners
        change_btn_text = "Змінити фото в запиті допомоги"
        change_btn_callback = self.form_admin_callback(action="ChangeNeedHelpPhoto")
        need_help_photo_change_btn = InlineKeyboardButton(change_btn_text, callback_data=change_btn_callback)

        change_btn_text = "Змінити інфо в партнерах"
        change_btn_callback = self.form_admin_callback(action="ChangePartnersMenuInfo")
        partners_menu_info_change_btn = InlineKeyboardButton(change_btn_text, callback_data=change_btn_callback)

        admin_markup.add(need_help_photo_change_btn, partners_menu_info_change_btn)

        # Add partner
        add_partner_btn_text = "Добавити партнера"
        add_partner_btn_callback = self.form_admin_callback(action="AddPartner")
        add_partner_btn = InlineKeyboardButton(add_partner_btn_text, callback_data=add_partner_btn_callback)
        admin_markup.add(add_partner_btn)
        

        if call is None:
            self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID,
                                  text="КУКУ адмін", reply_markup=admin_markup, parse_mode="HTML")
        else:
            message_id = call.message.message_id
            self.bot.edit_message_text(chat_id=self.data.ADMIN_CHAT_ID, message_id=message_id, text="КУКУ адмін", reply_markup=admin_markup)

    def send_team_list(self, call):
        message_id = call.message.message_id

        text = "Виберіть команду для перегляду детальнішої інформації"
        markup = InlineKeyboardMarkup()
        
        team_list = self.data.get_team()
        for team in team_list:
            btn_text = team["name"]
            btn_callback = self.form_admin_callback(action="TeamDetail", team_name=team["name"])
            btn = InlineKeyboardButton(btn_text, callback_data=btn_callback)
            markup.add(btn)

        # Back btn
        btn_text = "----------Назад----------"
        btn_callback = self.form_admin_callback(action="Hack")
        btn = InlineKeyboardButton(btn_text, callback_data=btn_callback)
        markup.add(btn)

        self.bot.edit_message_text(chat_id=self.data.ADMIN_CHAT_ID, message_id=message_id, text=text, reply_markup=markup)

    def send_team_detail(self, call, team_name):
        markup = InlineKeyboardMarkup()

        # Send Message
        btn_text = "Надіслати повідомлення команді"
        btn_callback = self.form_admin_callback(action="SendMessageToTeam", team_name=team_name)
        btn = InlineKeyboardButton(btn_text, callback_data=btn_callback)
        markup.add(btn)

        # Change Buttons
        change_task_btn_text = "Змінити таск"
        change_task_btn_callback = self.form_admin_callback("ChangeTeamTask", team_name=team_name)
        change_task_btn = InlineKeyboardButton(change_task_btn_text, callback_data=change_task_btn_callback)
        
        #change_partner_task_btn_text = "Змінити таск партнерів"
        #change_partner_task_btn_callback = self.form_admin_callback("ChangeTeamPartnerTask", team_name=team_name)
        #change_partner_task_btn = InlineKeyboardButton(change_partner_task_btn_text, callback_data=change_partner_task_btn_callback)
        markup.add(change_task_btn)

        # Show Tasks
        btn_text = "Показати поточні завдання"
        btn_callback = self.form_admin_callback(action="SendTeamTasks", team_name=team_name)
        btn = InlineKeyboardButton(btn_text, callback_data=btn_callback)
        markup.add(btn)

        # Delete Team
        #btn_text = "Видалити команду"
        #btn_callback = self.form_admin_callback(action="DeleteTeam", team_name=team_name)
        #btn = InlineKeyboardButton(btn_text, callback_data=btn_callback)
        #markup.add(btn)

        # Back Button
        btn_text = "----------Назад----------"
        btn_callback = self.form_admin_callback(action="TeamList")
        btn = InlineKeyboardButton(btn_text, callback_data=btn_callback)
        markup.add(btn)


        # Info about team
        team = self.data.get_team(where={"name":team_name}).next()
        members = self.hackathon.get_team_member_usernames_list(team=team)
        text = (f"<b>Команда</b> - {team['name']}\n"
                f"<b>Учасники</b> - {members}\n"
                f"<b>Дата реєстрації - </b>{team['register_date']}")


        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=text, reply_markup=markup, parse_mode="HTML")

    def send_team_tasks(self, call, team_name):
        team = self.data.get_team(where={"name":team_name}).next()

        # Normal task
        task_photo = team["task_photo"]
        task_text = team["task_text"]
        self.bot.send_photo(chat_id=self.data.ADMIN_CHAT_ID, photo=task_photo, caption=task_text, parse_mode="HTML")

        # Partner task
        #partner_task_photo = team["partner_task_photo"]
        #partner_task_text = team["partner_task_text"]
        #partner_task_link = team["partner_task_link"]
        #
        #markup = None
        #if partner_task_link:
        #    markup = InlineKeyboardMarkup()
        #    link_text = "Натисни на мене"
        #    btn = InlineKeyboardButton(text=link_text, url=partner_task_link)
        #    markup.add(btn)
        #
        #try:
        #    self.bot.send_photo(chat_id=self.data.ADMIN_CHAT_ID, photo=partner_task_photo, caption=partner_task_text, 
        #                        reply_markup=markup, parse_mode="HTML")
        #except:
        #    self.bot.send_photo(chat_id=self.data.ADMIN_CHAT_ID, photo=partner_task_photo, 
        #                        caption=partner_task_text, parse_mode="HTML")

        # Send previous menu
        self.send_team_detail(call, team_name)
    


    def send_admin_message_to_team(self, team_name):
        text_to_admin = f"Надішли мені повідомлення і я надішлю його команді <b>{team_name}</b>!"
        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=text_to_admin, parse_mode="HTML")

        self.bot.register_next_step_handler_by_chat_id(self.data.ADMIN_CHAT_ID, self.process_send_message,
                                                       destination="TEAM", team_name=team_name)

    def send_admin_message_to_all(self):
        text_to_admin = "Надішли мені повідомлення і я надішлю його всім користувачам бота!"
        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=text_to_admin, parse_mode="HTML")

        self.bot.register_next_step_handler_by_chat_id(self.data.ADMIN_CHAT_ID, self.process_send_message,
                                                       destination="ALL")

    def process_send_message(self, message, **kwargs):
        destination = kwargs["destination"]
        text = None
        photo = None

        content_type = message.content_type
        if content_type == "text":
            text = message.text
        elif content_type == "photo":
            text = message.caption
            photo = message.photo[-1].file_id
        else:
            if destination == "ALL":
                self.send_admin_message_to_all()
            elif destination == "TEAM":
                team_name = kwargs["team_name"]
                self.send_admin_message_to_team(team_name)
            return

        if destination == "ALL":
            users = self.data.get_user()
        elif destination == "TEAM":
            team_name = kwargs["team_name"]
            team_id = self.data.get_team(where={"name":team_name}).next()['_id']
            users = self.data.get_user(where={"team_id":team_id})
 
        for user in users:
            user_chat_id = user["chat_id"]
            try:
                if photo is None:
                    self.bot.send_message(chat_id=user_chat_id, text=text, parse_mode="HTML")
                else:
                    self.bot.send_photo(chat_id=user_chat_id, caption=text, photo=photo, parse_mode="HTML")
            except:
                continue


    def form_admin_callback(self, action, team_name=None):
        return f"Admin;{action};{team_name}"
