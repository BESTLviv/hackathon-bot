import configparser
from pymongo import MongoClient
from datetime import datetime
import hackathon
#dnspython

config = configparser.ConfigParser()
config.read('Settings.ini')

class Data:

    DESTROY_PASSWORD = "Кіт, ти маму мав????? -_-"

    def __init__(self, bot):
        self.ADMIN_CHAT_ID = -423275728
        self.TEST_PHOTO = "AgACAgIAAxkBAAMKX5VSJIaxHuz0-1ltpFW0JBj_ISkAAhmwMRtZJahIV_2nbh0WwcWSxg6YLgADAQADAgADbQADCDkCAAEbBA"

        self.bot = bot

        client = MongoClient(config['Mongo']['db'])
        db = client.test
        
        self.user_collection = db.user
        self.team_collection = db.team
        self.hackathon_collection = db.hackathon
        #self.partner_ad_collection = db.partner_addata.py

    def get_user(self, where=dict()):
        try:
            users = self.user_collection.find(where)
        except:
            users = None

        return users

    def add_user(self, name, surname, username, chat_id,
                 click_count=1, 
                 last_interaction_time=datetime.now(),
                 team_id=None, register_date=datetime.now()):
        
        _id = self.user_collection.insert_one({"name":name, "surname":surname, 
                                                 "username":username, "chat_id":chat_id,
                                                 "click_count":click_count,
                                                 "last_interaction_time":last_interaction_time,
                                                 "team_id":team_id, "register_date":register_date})

        return _id

    def update_user(self, set_:dict(), where:dict()):
        self.user_collection.update_one(where, {"$set":set_})

    def get_team(self, where=dict()):
        try:
            team = self.team_collection.find(where)
        except:
            team = None

        return team

    def add_team(self, name, task_photo=None, task_text=None,
                 partner_task_photo=None, partner_task_text=None,
                 partner_task_link=None,
                 register_date=datetime.now()):
        
        if task_photo is None:
            task_photo = self.TEST_PHOTO
            partner_task_photo = self.TEST_PHOTO

        _id = self.team_collection.insert_one({"name":name, "task_photo":task_photo, "task_text":task_text,
                                               "partner_task_photo":partner_task_photo, 
                                               "partner_task_text":partner_task_text,
                                               "partner_task_link":partner_task_link,
                                               "register_date":register_date})

        return _id.inserted_id

    def update_team(self, set_:dict(), where:dict()):
        self.team_collection.update_one(where, {"$set":set_})

    def get_hackathon(self, where=dict()):
        try:
            hackathon = self.hackathon_collection.find(where)
        except:
            hackathon = None

        return hackathon

    def add_hackathon(self, name, photo=None, schedule_photo=None, time_photo=None,
                      description=None, planned_date=None, start_time=None, end_time=None, 
                      registration_form = "sinoptik.ua",
                      status=0):
        
        #self.hackathon_collection.delete_many({"name":"Hello Hackathon!"})
        if photo is None:
            photo = self.TEST_PHOTO
            schedule_photo = self.TEST_PHOTO
            time_photo = self.TEST_PHOTO
        
        _id = self.hackathon_collection.insert_one({"name":name, "photo":photo,
                                                    "schedule_photo":schedule_photo,
                                                    "time_photo":time_photo,
                                                    "description":description,
                                                    "planned_date":planned_date,
                                                    "start_time":start_time, "end_time":end_time,
                                                    "registration_form":registration_form,
                                                    "status":status})

        return _id

    def update_hackathon(self, set_:dict()):
        self.hackathon_collection.update_one({}, {"$set":set_})
    
    def get_partner_ad(self, where=dict()):
        try:
            partner_ad = self.partner_ad_collection.find(where)
        except:
            partner_ad = None

        return partner_ad

    def add_partner_ad(self, name, register_date=datetime.now()):
        
        _id = self.partner_ad_collection.insert_one({"name":name, "register_date":register_date})

        return _id

    def update_partner_ad(self, set_:dict(), where:dict()):
        self.partner_ad_collection.update_one(where, {"$set":set_})
    
    def destroy_all(self):
        self.user_collection.remove()
        self.team_collection.remove()
        
        self.hackathon_collection.remove()