import streaming.collection.tweets
import streaming.collection.countries_api
import streaming.collection.covid19_api
import streaming.collection.crawler_facebook
import streaming.collection.crawler_facebook
import streaming.collection.articles

from streaming.collection.config_auth_twitter import *
import twitter

def authenticate(consumer_key= consumer_key, consumer_secret=consumer_secret, access_token_key=access_token_key, access_token_secret=access_token_secret, **kwargs):
    api = twitter.Api(consumer_key,consumer_secret,access_token_key,access_token_secret)
    return api