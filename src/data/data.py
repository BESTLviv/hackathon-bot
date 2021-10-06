from telebot import TeleBot
from telegraph import Telegraph
import mongoengine as me
from datetime import datetime, timezone, date

import string
import random


from .quiz import Question, Quiz
from ..data import hackathon as hack_db


class Data:

    TEST_PHOTO = "https://i.ibb.co/0Gv4JyW/photo-2021-04-16-12-48-15.jpg"

    def __init__(self, conn_string: str, bot: TeleBot):
        self.bot = bot

        me.connect(host=conn_string)
        print("connection success ")

        self.create_system_tables()

        self.hackathon: hack_db.Hackathon = self.get_hackathon()

    @property
    def start_quiz(self) -> Quiz:
        return Quiz.objects.filter(name="StartQuiz").first()

    @property
    def register_team_quiz(self) -> Quiz:
        return Quiz.objects.filter(name="RegisterTeamQuiz").first()

    @property
    def login_team_quiz(self) -> Quiz:
        return Quiz.objects.filter(name="LoginTeamQuiz").first()

    @property
    def cv_count(self) -> int:
        return User.objects.filter(cv_file_id__ne=None).count()

    def create_system_tables(self):
        self._create_quizes()

        self._create_hackathon()

    def _create_quizes(self):
        if Quiz.objects.filter(name="StartQuiz").count() == 0:
            self._create_start_quiz()

        if Quiz.objects.filter(name="RegisterTeamQuiz").count() == 0:
            self._create_register_team_quiz()

        if Quiz.objects.filter(name="LoginTeamQuiz").count() == 0:
            self._create_login_team_quiz()

    def _create_start_quiz(self):

        quiz = Quiz(name="StartQuiz", is_required=True)

        q_name_surname = Question(
            name="name_surname",
            message="Як мені до тебе звертатися?",
            correct_answer_message="Гарно звучить 🥰",
            wrong_answer_message="Введи ім’я текстом 🤡",
        )

        q_age = Question(
            name="age",
            message="Скільки тобі років?",
            regex="[1-9][0-9]",
            correct_answer_message="Ого, ми однолітки 🥰",
            wrong_answer_message="Вкажи свій справжній вік 🤡",
        )

        q_school = Question(
            name="school",
            message="Де вчишся? Вибери або введи.",
            buttons=[
                "НУЛП",
                "ЛНУ",
                "УКУ",
                "КПІ",
                "КНУ",
                "Ще в школі",
                "Вже закінчив(-ла)",
            ],
            correct_answer_message="Клас 🥰",
            wrong_answer_message="Введи назву текстом 🤡",
        )

        q_study_term = Question(
            name="study_term",
            message="Який ти курс?",
            buttons=[
                "Перший",
                "Другий",
                "Третій",
                "Четвертий",
                "На магістартурі",
                "Нічого з переліченого",
            ],
            allow_user_input=False,
            correct_answer_message="Ідеальний час, щоб будувати кар'єру 🥰",
            wrong_answer_message="Вибери, будь ласка, один з варіантів 🤡",
        )

        ##############
        q_city = Question(
            name="city",
            message="Звідки ти? Вибери зі списку або введи назву.",
            buttons=["Львів", "Київ", "Новояворівськ", "Донецьк", "Стамбул"],
            correct_answer_message="Був-був там!",
            wrong_answer_message="Введи назву текстом :)",
        )

        q_contact = Question(
            name="contact",
            message="Обміняємося контактами?",
            buttons=["Тримай!"],
            input_type="contact",
            correct_answer_message="Дякую. А я залишаю тобі контакт головного організатора: @Slavkoooo 🥰",
            wrong_answer_message="Надішли, будь ласка, свій контакт 🤡",
        )

        q_email = Question(
            name="email",
            message="Наостанок, вкажи адресу своєї поштової скриньки.",
            regex="^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$",
            correct_answer_message="Дякую 🥰",
            wrong_answer_message="Введи, будь ласка, електронну адресу 🤡",
        )

        q_agree = Question(
            name="user_agreements",
            message="Залишилося тільки дати згоду на обробку даних.",
            buttons=["Я погоджуюсь."],
            allow_user_input=False,
        )

        q_register_end = Question(
            name="end_register",
            message="Хух, усі формальності позаду!\n\nЯ зареєстрував тебе на ІЯК. Далі нас очікують два дні пригод.\n\n<b>Поонлайнимо?</b> 🤓",
            buttons=[
                "Прийду подивитися 👀",
                "Прийду шукати роботу 🤑",
                "Прийду дізнатися щось нове 🧐",
                "Візьму участь у воркшопах✍️",
                "Все разом 🤹",
            ],
            allow_user_input=False,
        )

        quiz.questions = [
            q_name_surname,
            q_age,
            q_school,
            q_study_term,
            # q_city,
            q_contact,
            q_email,
            q_agree,
            q_register_end,
        ]

        quiz.save()
        print("StartQuiz has been added")

    def _create_register_team_quiz(self):
        quiz = Quiz(name="RegisterTeamQuiz", is_required=False)

        q_team_name = Question(
            name="team_name",
            message="Напиши мені назву своєї команди",
            correct_answer_message="It is fucking amazing!",
            wrong_answer_message="Введи назву текстом 🤡",
        )

        q_password = Question(
            name="password",
            message="Придумай пароль для входу в твою команду",
            correct_answer_message="It is fucking amazing!",
            wrong_answer_message="Введи пароль текстом 🤡",
        )

        quiz.questions = [q_team_name, q_password]
        quiz.save()

        print("RegisterTeamQuiz has been added")

    def _create_login_team_quiz(self):
        quiz = Quiz(name="LoginTeamQuiz", is_required=False)

        q_login = Question(
            name="login",
            message="Введи логін",
            correct_answer_message="It is fucking amazing!",
            wrong_answer_message="Такий логін не зареєстрований у системі.",
        )

        q_password = Question(
            name="password",
            message="Введи пароль",
            correct_answer_message="It is fucking amazing!",
            wrong_answer_message="Пароль невірний. Спробуй ще раз",
        )

        quiz.questions = [q_login, q_password]
        quiz.save()

        print("LoginTeamQuiz has been added")

    def _create_hackathon(self):

        if hack_db.Hackathon.objects.first():
            print("Hack table is already exists")
            return

        hack_db.add_test_data()

    def update_quiz_table(self):
        quizes = Quiz.objects

        # form paragraphs in questions
        for quiz in quizes:
            for question in quiz.questions:
                question.message = question.message.replace("\\n", "\n")

            quiz.save()

    def get_hackathon(self) -> hack_db.Hackathon:
        return hack_db.Hackathon.objects.first()


class Content(me.Document):
    start_text = me.StringField()
    start_photo = me.StringField()
    user_start_text = me.StringField()
    user_start_photo = me.StringField()
    hack_start_text = me.StringField()
    hack_start_photo = me.StringField()
