import pyodbc

class Data:
    def __init__(self, bot):
        self.ADMIN_CHAT_ID = -423275728
        self.TEST_PHOTO = "AgACAgIAAxkBAAMKX5VSJIaxHuz0-1ltpFW0JBj_ISkAAhmwMRtZJahIV_2nbh0WwcWSxg6YLgADAQADAgADbQADCDkCAAEbBA"
        self.bot = bot

        self.message = Message()

    # TODO
    # 1) connect to DB (sqlite??)
    # 2) write get set update for every table
    
class Message:
    def __init__(self):
        self._init_messages()

    def _init_messages(self):
        ##############    ETC  #####################

        self.oops = "Щось пішло не так :("
        self.under_development = "В розробці"
        self.delete_error = "Старі повідомлення неможливо видалити"