from datetime import datetime, timezone

import mongoengine as me


class Team(me.Document):
    name = me.StringField(required=True)
    password = me.StringField(required=True)
    photo = me.StringField()
    registration_datetime = me.DateTimeField(required=True)
    is_active = me.BooleanField(default=False)

    def get_members(self):
        return [user.username for user in User.objects.filter(team=self)]


class User(me.Document):
    chat_id = me.IntField(required=True, unique=True)
    name = me.StringField(required=True)
    surname = me.StringField(required=True)
    username = me.StringField(required=True)
    cv_file_id = me.StringField(default=None)
    cv_file_name = me.StringField(default=None)
    additional_info = me.DictField(default=None)
    team: Team = me.ReferenceField(Team, required=False)
    register_source = me.StringField(default="Unknown")
    registration_date = me.DateTimeField(required=True)
    last_update_date = me.DateTimeField(required=True)
    last_interaction_date = me.DateTimeField(required=True)
    is_blocked = me.BooleanField(default=False)
    blocked_date = me.DateTimeField()

    @property
    def is_registered(self) -> bool:
        return self.additional_info != None

    def is_participant(self):
        if self.team:
            if self.team.is_active:
                return True

        return False

    def leave_team(self):
        self.team = None
        self.save()
