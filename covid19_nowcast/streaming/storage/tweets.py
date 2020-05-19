import pymongo.errors

tweets_col_name="tweets"

def init_collection(db,tweets_col_name=tweets_col_name):
    db[tweets_col_name].create_index("id_str", unique=True)
    return {}

def save(tweets,db, tweets_col_name=tweets_col_name):
    tweets_col = db[tweets_col_name]
    for tweet in tweets:
        try:
            tweets_col.insert_one(tweet)
        except pymongo.errors.DuplicateKeyError:
            print(tweet, "is already in database")
    return {}

def get(db, tweets_col_name=tweets_col_name):

    return {"tweets":list(db[tweets_col_name].find({},{ "_id": 0 }))}