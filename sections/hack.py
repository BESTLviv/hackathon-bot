from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from sections.section import Section

class Hack(Section):
    def __init__(self, data):
        super().__init__(data=data)

    def process_callback(self, call):
        #Hack;{action};{hack_id};{prev_msg_action}
        action, hack_id = call.data.split(";")[1:3]

        if action == "HackList":
            self.send_hack_list(call=call)

        elif action == "Menu":
            self.send_hack_menu(call, hack_id=hack_id)

        elif action == "Schedule":
            self.send_hack_schedule(call, hack_id=hack_id)

        elif action == "Partners":
            self.send_hack_partners(call, hack_id=hack_id)

        elif action == "Tasks":
            self.send_hack_tasks(call, hack_id=hack_id)

        elif action == "NeedHelp":
            self.send_need_help(call, hack_id=hack_id)

        elif action == "TimeLeft":
            self.send_time_left(call, hack_id=hack_id)

        else:
            self.in_development(call)
            return

        self.bot.answer_callback_query(call.id)

    def send_hack_list(self, call):
        chat_id = call.message.chat.id

        text = "Вибирай хак!"
        markup = InlineKeyboardMarkup()

        # Hack buttons
        for year in range(2020, 2017, -1):
            hack_btn_text = f"Hackaton {year}"
            hack_btn_callback = self.form_hack_callback(action="Menu", hack_id=year, prev_msg_action="Delete")
            hack_btn = InlineKeyboardButton(text=hack_btn_text, callback_data=hack_btn_callback)
            markup.add(hack_btn)

        # Back button
        back_button_callback = self.form_main_callback(action="Start", prev_msg_action="Delete")
        back_button = self.create_back_button(callback_data=back_button_callback)
        markup.add(back_button)

        self.send_message(call=call, text=text, reply_markup=markup)

    def send_hack_menu(self, call, hack_id):
        chat_id = call.message.chat.id

        text = f"<b>Hackathon {hack_id}</b>\n\n<b>Статус</b> - Триває\n<b>Твоя команда</b> - Сосунки"
        photo = self.data.TEST_PHOTO
        markup = InlineKeyboardMarkup()

        # Register button
        register_btn_text = f"Форма реєстрації"
        register_btn = InlineKeyboardButton(text=register_btn_text, url="https://www.google.com/forms/about/")
        markup.add(register_btn)

        ################## IF Status is "Running"
        # Schedule button
        schedule_btn_text = f"Розклад"
        schedule_btn_callback = self.form_hack_callback(action="Schedule", hack_id=hack_id, prev_msg_action="Delete")
        schedule_btn = InlineKeyboardButton(text=schedule_btn_text, callback_data=schedule_btn_callback)
        markup.add(schedule_btn)

        # Partners button
        partner_btn_text = f"Партнери"
        partner_btn_callback = self.form_hack_callback(action="Partners", hack_id=hack_id, prev_msg_action="Delete")
        partner_btn = InlineKeyboardButton(text=partner_btn_text, callback_data=partner_btn_callback)
        markup.add(partner_btn)

        # My tasks button
        task_btn_text = f"Мої завдання"
        task_btn_callback = self.form_hack_callback(action="Tasks", hack_id=hack_id, prev_msg_action="Delete")
        task_btn = InlineKeyboardButton(text=task_btn_text, callback_data=task_btn_callback)
        markup.add(task_btn)

        # Help & Time buttons
        help_btn_text = f"Потрібна допомога"
        help_btn_callback = self.form_hack_callback(action="NeedHelp", hack_id=hack_id)
        help_btn = InlineKeyboardButton(text=help_btn_text, callback_data=help_btn_callback)
        time_left_btn_text = f"Час"
        time_left_btn_callback = self.form_hack_callback(action="TimeLeft", hack_id=hack_id)
        time_left_btn = InlineKeyboardButton(text=time_left_btn_text, callback_data=time_left_btn_callback)
        markup.add(help_btn, time_left_btn)


        # Back button
        back_button_callback = self.form_hack_callback(action="HackList", prev_msg_action="Delete")
        back_button = self.create_back_button(callback_data=back_button_callback)
        markup.add(back_button)


        self.send_message(call=call, text=text, photo=photo, reply_markup=markup)

    def send_hack_schedule(self, call, hack_id):
        chat_id = call.message.chat.id

        text = f"<b>Зараз</b> - *що зараз*"
        photo = self.data.TEST_PHOTO
        markup = InlineKeyboardMarkup()

        # Back button
        back_button_callback = self.form_hack_callback(action="Menu", prev_msg_action="Delete")
        back_button = self.create_back_button(callback_data=back_button_callback)
        markup.add(back_button)

        self.send_message(call=call, text=text, photo=photo, reply_markup=markup)

    def send_hack_partners(self, call, hack_id):
        self.in_development(call)

    def send_hack_tasks(self, call, hack_id):
        self.in_development(call) 

    def send_need_help(self, call, hack_id):
        chat_id = call.message.chat.id

        text_to_user = f"Зараз до вас підійдуть!"
        self.bot.send_message(chat_id=chat_id, text=text_to_user, parse_mode="HTML")

        text_to_admin = f"Команда <b>Сосунки</b> потребують допомоги!"
        self.bot.send_message(chat_id=self.data.ADMIN_CHAT_ID, text=text_to_admin, parse_mode="HTML")

    def send_time_left(self, call, hack_id):
        chat_id = call.message.chat.id

        text = f"Часу залишилось - 15год 45хв"
        self.bot.answer_callback_query(call.id, text=text)
        #self.bot.send_message(chat_id=chat_id, text=text_to_user, parse_mode="HTML")