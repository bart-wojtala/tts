from models import Donation
from pymongo import MongoClient


class DatabaseClient:
    connection_string = 'mongodb://localhost:27017/'
    database_name = 'tts'
    messages_collection_name = 'messages'

    def __init__(self):
        self.client = MongoClient(self.connection_string)
        self.database = self.client[self.database_name]
        self.messages_collection = self.database[self.messages_collection_name]

    def add_message(self, donation):
        query = donation.__dict__
        newvalues = {"$set": donation.__dict__}
        self.messages_collection.update_one(query, newvalues, upsert=True)

    def get_first_message_in_queue(self):
        donation = self.messages_collection.find_one()
        return Donation(donation['messageId'], donation['name'], donation['message'])

    def delete_message(self, messageId):
        self.messages_collection.delete_one({'messageId': messageId})

    def is_messages_collection_not_empty(self):
        return False if self.messages_collection.count_documents({}) == 0 else True
