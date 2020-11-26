from models import Donation
from pymongo import MongoClient


class DatabaseClient:
    connection_string = 'mongodb://localhost:27017/'
    database_name = 'tts'
    donations_collection_name = 'donations'

    def __init__(self):
        self.client = MongoClient(self.connection_string)
        self.database = self.client[self.database_name]
        self.donations_collection = self.database[self.donations_collection_name]

    def add_donation(self, donation):
        query = donation.__dict__
        newvalues = {"$set": donation.__dict__}
        self.donations_collection.update_one(query, newvalues, upsert=True)

    def get_first_donation_in_queue(self):
        donation = self.donations_collection.find_one()
        return Donation(donation['messageId'], donation['name'], donation['message'])

    def delete_donation(self, messageId):
        self.donations_collection.delete_one({'messageId': messageId})

    def is_donations_collection_not_empty(self):
        return False if self.donations_collection.count_documents({}) == 0 else True
