from models import Message
from pymongo import MongoClient


class DatabaseClient:
    connection_string = 'mongodb://localhost:27017/'
    database_name = 'tts'
    messages_collection_name = 'messages'
    generated_collection_name = 'generated'

    def __init__(self):
        self.client = MongoClient(self.connection_string)
        self.database = self.client[self.database_name]
        self.messages_collection = self.database[self.messages_collection_name]
        self.generated_collection = self.database[self.generated_collection_name]

    def add_message(self, message):
        query = message.__dict__
        newvalues = {"$set": message.__dict__}
        self.messages_collection.update_one(query, newvalues, upsert=True)

    def add_generated_message(self, message):
        query = message.__dict__
        newvalues = {"$set": message.__dict__}
        self.generated_collection.update_one(query, newvalues, upsert=True)

    def get_first_message_in_queue(self):
        message = self.messages_collection.find_one()
        return Message(message['messageId'], message['name'], message['text'])

    def delete_message(self, messageId):
        self.messages_collection.delete_one({'messageId': messageId})

    def is_messages_collection_not_empty(self):
        return False if self.messages_collection.count_documents({}) == 0 else True
