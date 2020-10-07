import covid19_nowcast.streaming.collection.tweets
import covid19_nowcast.streaming.collection.countries_api
import covid19_nowcast.streaming.collection.covid19_api
import covid19_nowcast.streaming.collection.crawler_facebook
import covid19_nowcast.streaming.collection.articles

from covid19_nowcast.streaming.collection.config_auth_twitter import *
import twitter
    
from twarc import Twarc

import searchtweets

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

def collect_twitter_data(country,lang,date_from,date_to,count):
    data=[]
    try:
        begin_date=datetime.strptime(date_from,"%Y-%m-%d")
    except ValueError:
        begin_date=datetime.strptime(date_from,"%Y-%m-%dT%H:%M:%SZ")
        date_from=date_from[:10]
    try:
        end_date=datetime.strptime(date_to,"%Y-%m-%d")
    except ValueError:
        end_date=datetime.strptime(date_to,"%Y-%m-%dT%H:%M:%SZ")
        date_to=date_to[:10]
    delta=timedelta(seconds=(end_date-begin_date).total_seconds()).days

    today=datetime.strftime(datetime.today(),"%Y-%m-%d")
    # Separate request timerange between 1:{intersection with "30 days before today"} and the 2:rest
    date_from_full_arch,date_cut_30daysfullarch,date_to_30days=separate_timerange(date_from,date_to,today,days_offset=-30)
    if date_from_full_arch is not None:
        sub_begin_date=datetime.strptime(date_from_full_arch,"%Y-%m-%d")
        sub_end_date=datetime.strptime(date_cut_30daysfullarch,"%Y-%m-%d")
        sub_delta=timedelta(seconds=(sub_end_date-sub_begin_date).total_seconds()).days
        ratio=sub_delta/delta
        count_full_arch=int(ratio*count)
        if count_full_arch>0:
            data.extend(collect_twitter_fullarchive_data(country,lang,date_from_full_arch,date_cut_30daysfullarch,count_full_arch))

    # Separate request timerange between 1:{intersection with "7 days before today"} and the 2:rest
    if date_to_30days is not None:
        date_from_month,date_cut_30_7days,date_to_7days=separate_timerange(date_cut_30daysfullarch,date_to_30days,today,days_offset=-7)
        if date_from_month is not None:
            sub_begin_date=datetime.strptime(date_from_month,"%Y-%m-%d")
            sub_end_date=datetime.strptime(date_cut_30_7days,"%Y-%m-%d")
            sub_delta=timedelta(seconds=(sub_end_date-sub_begin_date).total_seconds()).days
            ratio=sub_delta/delta
            count_month=int(ratio*count)
            if count_month>0:
                data.extend(collect_twitter_30days_data(country,lang,date_from_month,date_cut_30_7days,count_month))

        if date_to_7days is not None:
            sub_begin_date=datetime.strptime(date_cut_30_7days,"%Y-%m-%d")
            sub_end_date=datetime.strptime(date_to_7days,"%Y-%m-%d")
            sub_delta=timedelta(seconds=(sub_end_date-sub_begin_date).total_seconds()).days
            ratio=sub_delta/delta
            count_7days=int(ratio*count)
            if count_7days>0:
                data.extend(collect_twitter_standard_data(country,lang,date_cut_30_7days,date_to_7days,count_7days))

    return data

def separate_timerange(date_from, date_to, date_ref, days_offset):
    date_from_bef=None
    date_cut=None
    date_to_after=None

    cut_date=datetime.strptime(date_ref,"%Y-%m-%d")+timedelta(days=days_offset)
    cut_date=datetime.strftime(cut_date,"%Y-%m-%d")
    print("cut",cut_date)
    if date_from>=cut_date:
        date_cut=date_from
        date_to_after=date_to
    elif date_to<=cut_date:
        date_from_bef=date_from
        date_cut=date_to
    else:
        date_from_bef=date_from
        date_cut=cut_date
        date_to_after=date_to

    assert not(date_from_bef is None and date_to_after is None)
    return date_from_bef, date_cut, date_to_after

def collect_twitter_standard_data(country,lang,date_from,date_to,count):
    print("standard",date_from,date_to)
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
    print(nb_tweets,nb_batches,nb_days,batches)
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

credentials_path="covid19_nowcast/streaming/collection/"

def collect_twitter_30days_data(country,lang,date_from,date_to,count):
    data=[]
    print("30days",date_from,date_to)
    premium_search_args = searchtweets.load_credentials(credentials_path+"twitter_keys.yaml",
                                       yaml_key="search_tweets_30day_api",
                                       env_overwrite=False)
    print(premium_search_args)

    query = "{country} (corona OR coronavirus OR virus OR covid-19 OR covid19)".format(country=country["Country"])
    rule = searchtweets.gen_rule_payload(query, results_per_call=10, from_date=date_from, to_date=date_to)
    print(rule)

    rs = searchtweets.ResultStream(rule_payload=rule,
                  max_results=10,
                  **premium_search_args)
    print(rs)
    data=[{"id_str":tw["id_str"],"created_at":datetime.strftime(datetime.strptime(str(tw["created_at"]),"%a %b %d %H:%M:%S %z %Y"),"%Y-%m-%dT%H:%M:%SZ"),"full_text":tw["text"]} for tw in rs.stream()]
    return data

def collect_twitter_fullarchive_data(country,lang,date_from,date_to,count):
    data=[]
    print("full",date_from,date_to)
    premium_search_args = searchtweets.load_credentials(credentials_path+"twitter_keys.yaml",
                                       yaml_key="search_tweets_full_api",
                                       env_overwrite=False)
    print(premium_search_args)
    query = "{country} (corona OR coronavirus OR virus OR covid-19 OR covid19)".format(country=country["Country"])
    rule = searchtweets.gen_rule_payload(query, results_per_call=10, from_date=date_from, to_date=date_to)
    print(rule)

    rs = searchtweets.ResultStream(rule_payload=rule,
                  max_results=10,
                  **premium_search_args)
    print(rs)
    data=[{"id_str":tw["id_str"],"created_at":datetime.strftime(datetime.strptime(str(tw["created_at"]),"%a %b %d %H:%M:%S %z %Y"),"%Y-%m-%dT%H:%M:%SZ"),"full_text":tw["text"]} for tw in rs.stream()]
    return data