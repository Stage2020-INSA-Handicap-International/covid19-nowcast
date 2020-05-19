import covid19_nowcast.streaming.data_collection.tweets
from covid19_nowcast.streaming.data_collection.config_auth_twitter import *
import twitter

def authenticate(consumer_key= consumer_key, consumer_secret=consumer_secret, access_token_key=access_token_key, access_token_secret=access_token_secret):
    api = twitter.Api(consumer_key,consumer_secret,access_token_key,access_token_secret)
    return {"api":api}