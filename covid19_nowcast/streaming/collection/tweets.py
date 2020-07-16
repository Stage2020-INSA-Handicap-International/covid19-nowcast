import json
import urllib
import util
from streaming.collection import crawler_twitter

def search_from_terms(api, term, **kwargs):
    """
    Gets tweets from Twitter's api which are result from *raw_query*
    Input:
        - api: an Twitter api object from the python-twitter module
        - term: a string term for the Twitter request
    Output:
        - tweets: a list of tweets, results of the Twitter request
    """
    tweets=api.GetSearch(term=term)
    return tweets

def search_from_geocode(api, geocode, **kwargs):
    """
    Gets tweets from Twitter's api which are result from *raw_query*
    Input:
        - api: an Twitter api object from the python-twitter module
        - geocode: an object following this format { "|(|[ } float(lat), float(long), float(radius) {mi|km} { "|)|] } (e.g. either a string, tuple, or array) for example "15.2,14.2,5km"
    Output:
        - tweets: a list of tweets, results of the Twitter request
    """
    tweets=api.GetSearch(geocode=geocode)
    return tweets

def search_from_raw_query(api, raw_query, **kwargs):
    """
    Gets tweets from Twitter's api which are results from *raw_query*
    Input:
        - api: an Twitter api object from the python-twitter module
        - raw_query: a string corresponding to a raw Twitter query
    Output:
        - tweets: a list of tweets, results of the Twitter request
    """
    tweets=api.GetSearch(raw_query=raw_query)
    return tweets

def crawl_from_raw_query(raw_query, live, count, legacy=False, **kwargs):
    """
    Crawl tweets from Twitter which are results from *raw_query*
    Input:
        - api: an Twitter api object from the python-twitter module
        - raw_query: a string corresponding to a raw Twitter query
    Output:
        - tweets: a list of tweets, results of the Twitter request
    """
    formatted_query = urllib.parse.quote(raw_query, safe='')
    crawler= crawler_twitter.search_legacy if legacy else crawler_twitter.search 
    tweets=crawler(raw_query="/search?q="+formatted_query+("&f=live" if live else ""), count=count)
    return tweets

def get_from_file(filepath, **kwargs):
    """
    Gets tweets at *filepath*
    Input:
        - filepath: the path to the file containing tweets in a dictionary format
    Output:
        - tweets: a list of tweets imported from the file 
    """
    with open(filepath, "r") as file:
        return json.load(file)

