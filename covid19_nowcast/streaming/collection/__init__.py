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
from datetime import datetime, timedelta
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

def collect_twitter_standard_data(country,lang,date_from,date_to,count):
    #data=util.import_params("../output/topics_india_tw0.json")["tweets"]
    api=authenticate()
    raw_query="{country} AND (corona OR coronavirus OR virus OR covid-19 OR covid19)".format(country=country["Country"])

    date_begin=datetime.strptime(date_from,"%Y-%m-%d")
    date_end=datetime.strptime(date_to,"%Y-%m-%d")

    nb_tweets=count
    nb_batches=1+(count-1)//100
    nb_days=int(timedelta(seconds=(date_end-date_begin).total_seconds()).days)
    if nb_batches>nb_days:
        print("More tweets than crawlable in Standard API",nb_batches,"/",nb_days)
        nb_batches=nb_days
        nb_tweets=nb_days*100
    batches=[]

    while nb_tweets>0:
        batches.append(100 if nb_tweets > 100 else nb_tweets)
        nb_tweets-=100
    assert len(batches)==nb_batches

    delta=date_end-date_begin
    batch_delta=timedelta(seconds=delta.total_seconds()/nb_batches)

    batch_froms=[datetime.strftime(date_begin+x*batch_delta,"%Y-%m-%d") for x in range(nb_batches)]
    batch_tos=[datetime.strftime(date_begin+x*batch_delta,"%Y-%m-%d") for x in range(1,nb_batches+1)]
    batch_tos[-1]=date_to
    assert len(batch_froms)==len(batches)
    assert len(batch_froms)==len(batch_tos)

    data=[]
    for index, batch in enumerate(batches):
        full_query = "q={formatted_query}&result_type=recent&since={date_from}&lang={lang}&until={date_to}&count={count}".format(formatted_query=urllib.parse.quote(raw_query, safe=''),lang=lang,date_from=batch_froms[index],date_to=batch_tos[index],count=batch)
        print("full_query",full_query)
        data.extend(api.GetSearch(raw_query=full_query))
    data=[{"id_str":t.id_str,"created_at":datetime.strftime(datetime.strptime(str(t.created_at),"%a %b %d %H:%M:%S %z %Y"),"%Y-%m-%dT%H:%M:%SZ"),"full_text":t.text} for t in data]
    
    return data