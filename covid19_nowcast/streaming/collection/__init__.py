import covid19_nowcast.streaming.collection.tweets
import covid19_nowcast.streaming.collection.countries_api
import covid19_nowcast.streaming.collection.covid19_api
import covid19_nowcast.streaming.collection.crawler_facebook
import covid19_nowcast.streaming.collection.articles

from covid19_nowcast.streaming.collection.config_auth_twitter import *
import twitter
from covid19_nowcast import util
def authenticate(consumer_key= consumer_key, consumer_secret=consumer_secret, access_token_key=access_token_key, access_token_secret=access_token_secret, **kwargs):
    api = twitter.Api(consumer_key,consumer_secret,access_token_key,access_token_secret)
    return api

def collect_sts_data(country,source,date_from,date_to):
    data=util.import_params("../output/topics_india_tw0.json")["tweets"]
    return data