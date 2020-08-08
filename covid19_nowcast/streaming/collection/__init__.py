import covid19_nowcast.streaming.collection.tweets
import covid19_nowcast.streaming.collection.countries_api
import covid19_nowcast.streaming.collection.covid19_api
import covid19_nowcast.streaming.collection.crawler_facebook
import covid19_nowcast.streaming.collection.articles

from covid19_nowcast.streaming.collection.config_auth_twitter import *
import twitter
    
from twarc import Twarc

import urllib
from covid19_nowcast import util
from covid19_nowcast.streaming.models.twitter import Tweet
from datetime import datetime
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

def authenticate(consumer_key= consumer_key, consumer_secret=consumer_secret, access_token_key=access_token_key, access_token_secret=access_token_secret):
    api = twitter.Api(consumer_key,consumer_secret,access_token_key,access_token_secret)
    return api

def twarc_auth(consumer_key= consumer_key, consumer_secret=consumer_secret, access_token_key=access_token_key, access_token_secret=access_token_secret):
    return Twarc(consumer_key, consumer_secret, access_token_key, access_token_secret)

def hydrate(tweets):
    twarc=twarc_auth()
    tweets=twarc.hydrate([tw["id_str"] for tw in tweets])
    return tweets

def collect_twitter_data(country,lang,date_from,date_to):
    #data=util.import_params("../output/topics_india_tw0.json")["tweets"]
    api=authenticate()
    raw_query="{country} AND (corona OR coronavirus OR virus OR covid-19 OR covid19)".format(country=country["Country"])
    full_query = "q={formatted_query}&result_type=recent&since={date_from}&lang={lang}&until={date_to}&count=2".format(formatted_query=urllib.parse.quote(raw_query, safe=''),lang=lang,date_from=date_from,date_to=date_to)
    data=api.GetSearch(raw_query=full_query)
    data=[{"id_str":t.id_str,"created_at":datetime.strftime(datetime.strptime(str(t.created_at),"%a %b %d %H:%M:%S %z %Y"),"%Y-%m-%dT%H:%M:%SZ"),"full_text":t.text} for t in data]
    
    return data