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
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
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
            try:
                found.extend(WebDriverWait(driver, timeout=10).until(lambda d: found[-1].find_elements_by_xpath("./../../../following-sibling::div//article")[:1]))
                tweets.extend([parse_tweet(element) for element in found[-2:-1]])
                scroll(driver,found[-1])
                bar.update(min(len(tweets), count))
            except StaleElementReferenceException as e:
                print(e)
                found=[WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.CSS_SELECTOR, "article"))]
                scroll(driver,found[-1])
            except TimeoutException as e:
                print(e)
                break
    driver.quit()
    return tweets[:count]

def parse_tweet(element, selector="div[data-testid='tweet']"):
    tweet = element.find_element(By.CSS_SELECTOR, selector)
    if "Le propriétaire de ce compte limite qui peut voir ses Tweets." in element.text:
        return None
    parsed_tweet = Tweet(id_str=parse_id(tweet), user = parse_user(tweet), created_at = parse_date(tweet), full_text = parse_text(tweet), retweet_count = parse_retweets(tweet), favorite_count = parse_favorites(tweet), replies = parse_replies_count(tweet))
    # if parsed_tweet.replies>0:
    #     parsed_tweet.replies=parse_replies(element)
    # else :
    #     parsed_tweet.replies=[]
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

def parse_text(element, selector="./div[last()]/div[last()]", rm_strs=[r"Le média suivant comprend des contenus potentiellement sensibles\. Modifier les paramètres\nVoir",
                                                                        r"En réponse à \n@[a-z0-9_]*(\n  et  \n@[a-z0-9_]*)?\n"]):
    full_text=element.find_element_by_xpath(selector).text
    for rm_str in rm_strs:
        full_text=re.sub(rm_str,"",full_text)
    return full_text

def parse_retweets(element, selector="div[data-testid='like']"):
    count = element.find_element(By.CSS_SELECTOR, selector).text
    return int(count) if count != "" and count[-1]!="k" else 0 if count == "" else int(float(count.replace(",", ".")[:-2])*1000)

def parse_favorites(element, selector="div[data-testid='retweet']"):
    count = element.find_element(By.CSS_SELECTOR, selector).text
    return int(count) if count != "" and count[-1]!="k" else 0 if count == "" else int(float(count.replace(",", ".")[:-2])*1000)

def parse_replies_count(element, selector="div[data-testid='reply']"):
    count = element.find_element(By.CSS_SELECTOR, selector).text
    return int(count) if count != "" and count[-1]!="k" else 0 if count == "" else int(float(count.replace(",", ".")[:-2])*1000)

def parse_replies(element, selector=".//time/.."):
    link = element.find_element_by_xpath(selector).get_attribute("href")
    driver = webdriver.Firefox()
    driver.get(link) 
    replies=[]
    found=[WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.CSS_SELECTOR, "article"))]
    #Get first response to the first found article which is the initial tweet
    found_beginning=len(found[-1].find_elements_by_xpath("./div/div/div/div"))==3

    while not found_beginning:
        found=WebDriverWait(driver, timeout=1).until(lambda d: found[-1].find_elements_by_xpath("./../../../following-sibling::div//article")[:1])
        if len(found[-1].find_elements_by_xpath("./div/div/div/div"))==3:
            found_beginning=True
    found=WebDriverWait(driver, timeout=1).until(lambda d: found[-1].find_elements_by_xpath("./../../../following-sibling::div//article")[:1])
    #found is now the first reply
    try:
        while True:#until it doesn't find a next tweet
            found.extend(WebDriverWait(driver, timeout=1).until(lambda d: found[-1].find_elements_by_xpath("./../../../following-sibling::div//article")[:1]))
            replies.extend([parse_tweet(element) for element in found[:-1]])
            found=[found[-1]]
            if is_thread(found[-1]):
                print("is_thread")
                while is_thread(found[-1]):
                    found=WebDriverWait(driver, timeout=1).until(lambda d: found[-1].find_elements_by_xpath("./../../../following-sibling::div//article")[:1])
                found=WebDriverWait(driver, timeout=1).until(lambda d: found[-1].find_elements_by_xpath("./../../../following-sibling::div//article")[:1])
            scroll(driver,found[-1])
    except TimeoutException:
        pass
    replies.append(parse_tweet(found[-1]))
    driver.quit()
    return replies

def is_thread(element, selector="./div/div/div/div[2]/div[1]/div"):
    print("e",element.find_elements_by_xpath(selector))
    print("c",parse_replies_count(element)>0)
    print("r", element.find_elements_by_xpath(selector)==2 and parse_replies_count(element)>0)
    return len(element.find_elements_by_xpath(selector))==2 and parse_replies_count(element)>0

def scroll(driver, element):
    # Scroll so that element is at the top of the page
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
