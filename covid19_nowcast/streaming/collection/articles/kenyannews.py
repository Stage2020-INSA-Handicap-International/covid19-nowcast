from covid19_nowcast.streaming.collection.articles.crawler import Crawler
from bs4 import BeautifulSoup
import requests
import sys
import json
import progressbar

from datetime import datetime
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

class KN_Crawler(Crawler):
    def __init__(self,categories_to_crawl=None, HI_category_nomenclature=False, parsed_urls=[]):
        if categories_to_crawl==None:
            categories_to_crawl=list(KN_Crawler.site_categories_to_ours.keys())
        super().__init__(KN_Crawler.root_url,categories_to_crawl,KN_Crawler.site_categories_to_ours,HI_category_nomenclature)

    def articles_from_site(self, link, separate=False):
        if separate:
            return [self.articles_from_category(self.root_url+link, category) for category, link in progressbar.progressbar(KN_Crawler.category_urls.items(), prefix=link)]
        else:
            for category, link in progressbar.progressbar([(cat, lnk) for cat,lnk in KN_Crawler.category_urls.items() if cat in self.categories_to_crawl], prefix=link):
                yield from self.articles_from_category(self.root_url+link, category)

    def articles_from_category(self, link, category):
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'lxml')
        links = [a.get("href") for a in soup.find_all("a") if link != a.get("href") and link in a.get("href")]
        links = list(set(links))
        for page_url in progressbar.progressbar(links, prefix=category):
            yield from self.parse_article(link+page_url, category)

    def parse_article(self, link, category):
        try:
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'lxml')
            details=soup
            text=[p.text for p in details.find_all("p")]
            author="N/A"
            date="N/A"#soup.find("span",{"class":"text-dt"}).text
            yield {"author":author,"created_at":date,"full_text":"\n".join(text), "category":category}
        except:
            print(link)
            yield None

KN_Crawler.root_url="https://kenyannews.co.ke/"
KN_Crawler.category_urls={
    "world-news":"world-news/",
    "politics":"news/politics/",
    "county-news":"news/county-news/",
    "africa-news":"news/africa-news/",
    "business":"business-news/",
    "entertainment":"entertainment/",
    "lifestyle":"lifestyle/",
    "health":"health/",
    "tech":"technology/",
    "sports":"sports/",
}
KN_Crawler.site_categories_to_ours={
    "world-news":"World",
    "politics":"Politics",
    "county-news":"World",
    "africa-news":"World",
    "business":"business-news/",
    "entertainment":"entertainment/",
    "lifestyle":"lifestyle/",
    "health":"health/",
    "tech":"technology/",
    "sports":"sports",
}