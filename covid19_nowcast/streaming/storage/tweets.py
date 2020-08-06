import pymongo.errors

tweets_col_name="tweets"
from covid19_nowcast.streaming.models import twitter
def init_collection(db,tweets_col_name=tweets_col_name):
    db[tweets_col_name].create_index({"id_str":1}, unique=True)
    db[tweets_col_name].create_index({"country":1,"source":1,"lang":1,"created_at":-1})

def save(tweets,db, tweets_col_name=tweets_col_name):
    tweets_col = db[tweets_col_name]
    for tweet in tweets:
        try:
            tweet=twitter.dehydrate(tweet)
            tweets_col.insert_one(tweet)
        except pymongo.errors.DuplicateKeyError:
            print(tweet, "is already in database")

def get(db, tweets_col_name=tweets_col_name):
    return list(db[tweets_col_name].find({},{ "_id": 0 }))