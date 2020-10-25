from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from sections.section import Section

class Main(Section):
    def __init__(self, data):
        super().__init__(data=data)

    def process_callback(self, call):
        action = call.data.split(";")[1]

        if action == "Start":
            self.send_start_message(call=call)

        elif action == "Special":
            self.in_development(call)

        elif action == "HowToUse":
            self.in_development(call)

        else:
            self.in_development(call)
            return

        self.bot.answer_callback_query(call.id)

    def send_start_message(self, chat_id=None, call=None):
        """Send start message with introduction to bot.\n
        Specify chat_id if it called through command, otherwise
        specify call if it called after button pressed.
        """
        text = "Привіт...Я бот хакатону від Бесту....Вмію робити то і то...."
        photo = self.data.TEST_PHOTO

        markup = InlineKeyboardMarkup()

        start_btn_text = "HACK IT!"
        start_btn_callback = self.form_hack_callback(action="HackList", prev_msg_action="Delete")
        start_btn = InlineKeyboardButton(text=start_btn_text, callback_data=start_btn_callback)
        markup.add(start_btn)

        if chat_id is not None:
            self.bot.send_photo(chat_id, caption=text, photo=photo, reply_markup=markup, parse_mode="HTML")
        else:
            self.send_message(call, text=text, photo=photo, reply_markup=markup)
