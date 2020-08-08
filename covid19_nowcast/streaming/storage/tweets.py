import pymongo.errors
import pymongo
from covid19_nowcast.streaming.storage.config_mongodb import *

from covid19_nowcast.streaming.models import twitter
def init_collection(db,tweets_col_name=col_data_analyses):
    db[tweets_col_name].create_index( [('id_str', pymongo.ASCENDING)], unique=True)
    db[tweets_col_name].create_index( [('country', pymongo.ASCENDING),('source', pymongo.ASCENDING),('lang', pymongo.ASCENDING),('created_at', pymongo.DESCENDING)])

def save(tweets,db, tweets_col_name=col_data_analyses):
    for d in tweets:
        db[tweets_col_name].update({"id_str":d["id_str"]},{**d},upsert=True)

def get(db, tweets_col_name=col_data_analyses):
    return list(db[col_data_analyses].find({},{ "_id": 0 }))
