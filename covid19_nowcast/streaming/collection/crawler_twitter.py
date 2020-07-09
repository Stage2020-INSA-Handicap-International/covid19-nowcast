# script to scrap tweets by a twitter user.
# Author - ThePythonDjango.Com
# dependencies - BeautifulSoup, requests

from bs4 import BeautifulSoup
import requests
import sys
import json
import progressbar

from datetime import datetime
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

def get_tweets_data(soup):
    tweets=[]
    for tweet_container in soup.find_all("table", {"class":"tweet"}):
        date = tweet_container.find("td", {"class":"timestamp"}).text.replace("\n","").strip()
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

    return tweets

def search_legacy(raw_query, count):
    tweets=[]
    next_url = raw_query
    with progressbar.ProgressBar(max_value=count, prefix="Tweets: ") as bar:
        while next_url is not None and len(tweets) < count:
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
            tweets.extend(get_tweets_data(soup))
            next_url=soup.find("div", {"class":"w-button-more"})
            if next_url is not None:
                next_url=next_url.a["href"]
            print(".", end="")
            sys.stdout.flush()

            bar.update(min(len(tweets),count))

    return tweets[:count]

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import progressbar
from streaming.models.twitter import Tweet
import re

def search(raw_query, count):
    driver = webdriver.Firefox()
    driver.get("https://twitter.com"+raw_query) 
    tweets=[]
    found=[WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.CSS_SELECTOR, "article"))]
    with progressbar.ProgressBar(max_value=count, prefix="Tweets: ") as bar:
        while len(tweets)<count:
            found.extend(WebDriverWait(driver, timeout=10).until(lambda d: found[-1].find_elements_by_xpath("./../../../following-sibling::div//article")[:1]))
            tweets.extend([parse_tweet(element) for element in found[:-1]])
            found=[found[-1]]
            scroll(driver,found[-1])
            bar.update(min(len(tweets), count))
    driver.quit()
    return tweets[:count]

def parse_tweet(element, selector="div[data-testid='tweet']"):
    tweet = element.find_element(By.CSS_SELECTOR, selector)
    parsed_tweet = Tweet(id_str=parse_id(tweet), user = parse_user(tweet), created_at = parse_date(tweet), full_text = parse_text(tweet), retweet_count = parse_retweets(tweet), favorite_count = parse_favorites(tweet), replies = parse_replies(tweet))
    return parsed_tweet.to_dict()

def parse_id(element, selector=".//time/.."):
    return re.search("[0-9]*$",element.find_element_by_xpath(selector).get_attribute("href")).group()

def parse_user(element, selector=".//time/../../div[position() = 1]/a/div"):
    user=element.find_element_by_xpath(selector)
    name=user.find_element_by_xpath("./div[position() = 1]").text
    screen_name=user.find_element_by_xpath("./div[position() = 2]").text
    return {"name":name, "screen_name":screen_name}

    
def parse_date(element, selector=".//time"):
    return element.find_element_by_xpath(selector).get_attribute("datetime").replace(".000Z", "+00:00").replace("T"," ")

def parse_text(element, selector="./div[last()]/div[last()]"):
    return element.find_element_by_xpath(selector).text

def parse_retweets(element, selector="div[data-testid='like']"):
    favorites = element.find_element(By.CSS_SELECTOR, selector).text
    return int(favorites) if favorites != "" else 0

def parse_favorites(element, selector="div[data-testid='retweet']"):
    favorites = element.find_element(By.CSS_SELECTOR, selector).text
    return int(favorites) if favorites != "" else 0

def parse_replies(element, selector="div[data-testid='reply']"):
    favorites = element.find_element(By.CSS_SELECTOR, selector).text
    return int(favorites) if favorites != "" else 0

def scroll(driver, element):
    # Scroll so that element is at the top of the page
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
