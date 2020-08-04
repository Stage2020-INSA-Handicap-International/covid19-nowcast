import pymongo
from covid19_nowcast.streaming.storage.config_mongodb import *
from covid19_nowcast.streaming.storage import tweets 

def init_database(connection_url=connection_url, db_name=db_name, **kwargs):
    db=pymongo.MongoClient(connection_url)[db_name]
    tweets.init_collection(db)
    return db

def connect_database(connection_url=connection_url, db_name=db_name, **kwargs):
    db=pymongo.MongoClient(connection_url)[db_name]
    return db