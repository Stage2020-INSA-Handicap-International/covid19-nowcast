# script to scrap tweets by a twitter user.
# Author - ThePythonDjango.Com
# dependencies - BeautifulSoup, requests

from bs4 import BeautifulSoup
import requests
import sys
import json

from datetime import datetime
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def get_tweets_data(soup):
    tweets=[]
    year_is_2020 = False
    year_is_2019 = False
    for tweet_container in soup.find_all("table", {"class":"tweet"}):
        date = tweet_container.find("td", {"class":"timestamp"}).text.replace("\n","").strip()
        #Since the crawled date doesn't contain the year, we detect the end of 2020 when the month switches from Jan to anything else
        #The crawling stops at that switch
        month = date.split(" ")[0]
        month_is_jan = (month == "Jan")
        if month_is_jan:
            year_is_2020 = True
        if year_is_2020 and not month_is_jan:
            year_is_2019 = True
            break
        try:
            date=datetime.strptime(date+" 2020",'%b %d %Y')
        except:
            date=datetime.now()
        date = datetime.strftime(date,'%a %b %d %H:%M:%S %z %Y').replace("  ", " +0000 ")

        tweets.append(
            {
                "created_at":str(
                    date
                ),
                "id_str":str(
                    tweet_container.find("div", {"class":"tweet-text"})["data-id"].strip()
                ),
                "full_text":str(
                    tweet_container.find("div", {"class":"dir-ltr"}).text.replace("\n","").strip()
                ),
                "user":{
                    "name": str(
                        tweet_container.find("strong", {"class":"fullname"}).text.strip()
                    ),
                    "screen_name": str(
                        tweet_container.find("div", {"class":"username"}).text.replace("\n","").replace("@", "").strip()
                    ),
                },
            }
        )

    return tweets,year_is_2019

def search(raw_query, count):
    tweets=[]
    next_url = raw_query
    year_is_2019 = False
    while (not year_is_2019) and next_url is not None and len(tweets) < count:
        response = None
        try:
            response = requests.get("https://mobile.twitter.com"+next_url)
        except Exception as e:
            print(repr(e))
            sys.exit(1)
        
        if response.status_code != 200:
            print("Non success status code returned "+str(response.status_code))
            sys.exit(1)

        soup = BeautifulSoup(response.text, 'lxml')
        one_page_tweets,year_is_2019 = get_tweets_data(soup)
        tweets.extend(one_page_tweets)
        next_url=soup.find("div", {"class":"w-button-more"})
        if next_url is not None:
            next_url=next_url.a["href"]
        print(".", end="")
        sys.stdout.flush()

    return tweets[:count]
