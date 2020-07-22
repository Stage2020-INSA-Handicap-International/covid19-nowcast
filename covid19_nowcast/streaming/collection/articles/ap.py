from streaming.collection.articles.crawler import Crawler
from bs4 import BeautifulSoup
import requests
import sys
import json
import progressbar

from datetime import datetime
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

class AP_Crawler(Crawler):
    def __init__(self,categories_to_crawl=None, parsed_urls=[]):
        if categories_to_crawl==None:
            categories_to_crawl=list(AP_Crawler.site_categories_to_ours.keys())
        super().__init__(AP_Crawler.root_url,categories_to_crawl,AP_Crawler.site_categories_to_ours)

    def articles_from_site(self, link, separate=False):
        if separate:
            return [self.articles_from_category(self.root_url+link, category) for category, link in progressbar.progressbar(AP_Crawler.category_urls.items(), prefix=link)]
        else:
            for category, link in progressbar.progressbar(AP_Crawler.category_urls.items(), prefix=link):
                yield from self.articles_from_category(self.root_url+link, category)

    def articles_from_category(self, link, category):
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'lxml')
        articles=soup.find("article")
        links = [a.find("a").get("href") for a in articles.find_all("div", {"data-key":"feed-card-wire-story-with-image"})]
        for page_url in progressbar.progressbar(links, prefix=category):
            yield from self.parse_article(link+page_url, category)

    def parse_article(self, link, category):
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'lxml')
        article=soup.find("article")
        if article is None:
            article=soup.find("div",{"data-key":"article"})
            assert(article is not None)
        title=soup.find("div", {"class":"headline-0-2-55"})
        if title is None:
            title=soup.find("div", {"data-key":"card-headline"})
            assert(title is not None)
            title=title.text
        text = [p.text for p in article.find_all("p")]
        date=soup.find("span",{"data-key":"timestamp"}).get("data-source")
        author=soup.find("span",{"class":"Component-bylines-0-2-61"})
        if author is None:
            author="N/A"
        else:
            author=author.text
        yield {"author":author,"created_at":date,"full_text":"\n".join(text), "category":category}

AP_Crawler.root_url="https://apnews.com/"
AP_Crawler.category_urls={
    "AP Top News":"/apf-topnews",
    "Sports":"/apf-sports",
    "Entertainment":"/apf-entertainment",
    "Lifestyle":"/apf-lifestyle",
    "Oddities":"/apf-oddities",
    "Photography":"/Photography",
    "Travel":"/apf-Travel",
    "Technology":"/apf-technology",
    "Business":"/apf-business",
    "U.S. News":"/apf-usnews",
    "Health":"/apf-Health",
    "Science":"/apf-science",
    "International News":"/apf-intlnews",
    "Politics":"/apf-politics",
    "Religion":"/apf-religion",
}
AP_Crawler.site_categories_to_ours={
    "AP Top News":"/apf-topnews",
    "Sports":"/apf-sports",
    "Entertainment":"/apf-entertainment",
    "Lifestyle":"/apf-lifestyle",
    "Oddities":"/apf-oddities",
    "Photography":"/Photography",
    "Travel":"/apf-Travel",
    "Technology":"/apf-technology",
    "Business":"/apf-business",
    "U.S. News":"/apf-usnews",
    "Health":"/apf-Health",
    "Science":"/apf-science",
    "International News":"/apf-intlnews",
    "Politics":"/apf-politics",
    "Religion":"/apf-religion",
}