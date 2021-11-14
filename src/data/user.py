from datetime import datetime, timezone

import mongoengine as me


class Resume(me.EmbeddedDocument):
    file_id = me.StringField(required=True)
    file_name = me.StringField(required=True)
    file_size = me.IntField(required=True)


class Team(me.Document):
    name = me.StringField(required=True)
    password = me.StringField(required=True)
    photo = me.StringField()
    registration_datetime = me.DateTimeField(required=True)
    test_task = me.StringField(required=False)
    test_task_passed = me.BooleanField(default=None)
    is_active = me.BooleanField(default=False)

    members: list

    @property
    def members(self):
        return [user for user in User.objects.filter(team=self)]

    @property
    def members_count(self) -> int:
        return User.objects.filter(team=self).count()

    def __init__(self, *args, **values):
        super().__init__(*args, **values)

    @property
    def test_task_status(self) -> tuple:
        if self.test_task is None and self.test_task_passed is None:
            return ("🕑", "не здано")

        if self.test_task and self.test_task_passed is None:
            return ("📝", f"на перевірці - <a href='{self.test_task}'>посилання</a>")

        if self.test_task and self.test_task_passed is False:
            return ("❌", f"не пройшли - <a href='{self.test_task}'>посилання</a>")

        if self.test_task_passed is True:
            return ("✅", f"здано - <a href='{self.test_task}'>посилання</a>")

        return ("❌", "не здано")

    @property
    def full_info(self) -> str:
        used_techs = "\n".join(
            [user.additional_info["tech_used"] for user in self.members]
        )
        return f"{self}\n\n" f"<b>Технології:</b>\n" f"{used_techs}"

    def __str__(self) -> str:
        members = self.members

        users_list = "\n".join([f"{user.name} - @{user.username}" for user in members])

        cv_list = "\n".join(
            [
                f"{user.name} - {user.resume.file_name if user.resume else 'резюме не надіслано.'}"
                for user in members
            ]
        )
        is_participate = "✅" if self.test_task_passed else "❌"

        team_name = str(self.name).replace("<", "*").replace(">", "*")
        return (
            f"Команда <b>{team_name}</b>\n\n"
            f"<b>Учасники команди:</b>\n"
            f"{users_list}\n\n"
            f"<b>Резюме:</b>\n"
            f"{cv_list}\n\n"
            f"<b>Тестове завдання</b> - {self.test_task_status[0]} ({self.test_task_status[1]})\n"
            f"<b>Команда бере участь в хакатоні</b> - {is_participate}"
        )


class User(me.Document):
    chat_id = me.IntField(required=True, unique=True)
    name = me.StringField(default=None)
    surname = me.StringField(default=None)
    username = me.StringField(default=None)
    resume = me.EmbeddedDocumentField(Resume, default=None)
    additional_info = me.DictField(default=None)
    team: Team = me.ReferenceField(Team, required=False)
    register_source = me.StringField(default="Unknown")
    registration_date = me.DateTimeField(required=True)
    last_update_date = me.DateTimeField(required=True)
    last_interaction_date = me.DateTimeField(required=True)
    is_blocked = me.BooleanField(default=False)
    blocked_date = me.DateTimeField(default=None)

    @property
    def is_registered(self) -> bool:
        return self.additional_info != None

    @property
    def is_participant(self):
        if self.team:
            if self.team.test_task_passed:
                return True

        return False

    def update_test_task(self, link: str):
        self.team.test_task = link
        self.team.save()

    def update_resume(self, user, container):
        resume = Resume(
            file_id=container["file_id"],
            file_name=container["file_name"],
            file_size=container["file_size"],
        )
        self.resume = resume
        self.save()

    def leave_team(self):
        self.team = None
        self.save()
