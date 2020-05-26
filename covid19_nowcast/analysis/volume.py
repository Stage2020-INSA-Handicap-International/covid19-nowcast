from datetime import datetime
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
from collections import Counter

def user_count(tweets, analyses={}, **kwargs):
    """
    Counts the number of unique users in input tweets
    Input:
        - tweets: a list of tweets in the form of dictionaries
        - analyses: container dictionary for analyses
    Output:
        - analyses: container dictionary for analyses with an added entry "user_count"
    """
    user_set={tweet["user"]["id_str"] for tweet in tweets}
    analyses["user_count"]=len(user_set)
    return {"analyses":analyses}

def tweets_per_day(tweets, analyses={}, **kwargs):
    """
    Counts tweets per day into a Counter(date) instance 
    Input:
        - tweets: a list of tweets in the form of dictionaries
        - analyses: container dictionary for analyses
    Output:
        - analyses: container dictionary for analyses with an added entry "tweets_per_day"
    """
    date_set=Counter(datetime.date(datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S %z %Y')) for tweet in tweets)
    analyses["tweets_per_day"]=date_set
    return {"analyses":analyses}

def tweets_per_country(tweets, analyses={}, **kwargs):
    """
    Counts tweets per country into a Counter(date) instance 
    Input:
        - tweets: a list of tweets in the form of dictionaries
        - analyses: container dictionary for analyses
    Output:
        - analyses: container dictionary for analyses with an added entry "tweets_per_country"
    """
    date_set=Counter(  tweet["user"].get("location", "N/A") for tweet in tweets)
    analyses["tweets_per_country"]=date_set
    return {"analyses":analyses}

def tweets_per_country_normalised_on_pop(tweets, countries_info, analyses={}, **kwargs):
    """
    Counts tweets per country divided by their population into a Counter(date) instance 
    Input:
        - tweets: a list of tweets in the form of dictionaries
        - analyses: container dictionary for analyses
    Output:
        - analyses: container dictionary for analyses with an added entry "tweets_per_country_normalised_on_pop"
    """
    date_set=Counter(  tweet["user"].get("location", "N/A") for tweet in tweets)
    print(date_set)
    input()
    date_set= {#**{date:count/[country["population"] for country in countries_info if country["alpha2Code"]==date][0] for date, count in date_set.items() if date != "N/A"}, 
                **{ date:count for date, count in date_set.items() if date == "N/A"}}
    analyses["tweets_per_country_normalised_on_pop"]=date_set
    return {"analyses":analyses}

def tweets_timeline(tweets, countries_covid19, analyses, **kwargs):
    """
    Concatenates infos on each day's Covid-19 situation in a country and the number of tweets that day
    Input:
        - tweets: a list of tweets in the form of dictionaries
        - analyses: container dictionary for analyses
    Output:
        - analyses: container dictionary for analyses with an added entry "timeline"
    """
    timeline={}
    date_set=Counter(datetime.date(datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S %z %Y')) for tweet in tweets)
    for country, country_covid19 in countries_covid19.items():
        timeline[country]={}
        for situation in country_covid19:
            if situation["Date"] in date_set:# TODO and correct country:
                timeline[country][situation["Date"]]={**situation,"tweet_count":date_set[situation["Date"]]}
    analyses["timeline"]=timeline
    return {"analyses":analyses}