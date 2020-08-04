from covid19_nowcast.streaming.collection.articles.crawler import Crawler
from bs4 import BeautifulSoup
import requests
import sys
import json
import progressbar
import re
from datetime import datetime
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

class NYT_Crawler(Crawler):
    def __init__(self,categories_to_crawl=None, HI_category_nomenclature=False, parsed_urls=[]):
        if categories_to_crawl==None:
            categories_to_crawl=list(NYT_Crawler.site_categories_to_ours.keys())
        super().__init__(NYT_Crawler.root_url,categories_to_crawl,NYT_Crawler.site_categories_to_ours,HI_category_nomenclature)

    def articles_from_site(self, link, separate=False):
        if separate:
            return [self.articles_from_category(self.root_url+link, category) for category, link in progressbar.progressbar(NYT_Crawler.category_urls.items(), prefix=link)]
        else:
            for category, link in progressbar.progressbar([(cat, lnk) for cat,lnk in NYT_Crawler.category_urls.items() if cat in self.categories_to_crawl], prefix=link):
                yield from self.articles_from_category(self.root_url+link, category)

    def articles_from_category(self, link, category):
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'lxml')
        links = [a.get("href") for a in soup.find_all("a") if re.search(r"/[a-z-]*/$",link).group() in a.get("href")]
        links = list(set(links))
        for page_url in progressbar.progressbar(links, prefix=category):
            yield from self.parse_article(self.root_url+page_url, category)

    def parse_article(self, link, category):
        try:
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'lxml')
            details=soup
            text=[p.text for p in details.find_all("p")]
            author="N/A"
            date="N/A"#soup.find("p",{"class":"news-article-header__timestamps-posted"}).text
            yield {"author":author,"created_at":date,"full_text":"\n".join(text), "category":category}
        except:
            print(link)
            yield None

NYT_Crawler.root_url="https://www.nytimes.com/"
NYT_Crawler.category_urls={
    "World":"section/world/",
    "U.S.":"section/us/",
    "Politics":"section/politics/",
    "N.Y.":"section/nyregion/",
    "Business":"section/business/",
    "Opinion":"section/opinion/",
    "Tech":"section/technology/",
    "Science":"section/science/",
    "Health":"section/health/",
    "Sports":"section/sports/",
    "Arts":"section/arts/",
    "Books":"section/books/",
    "Style":"section/style/",
    "Food":"section/food/",
    "Travel":"section/travel/",
    "Magazine":"section/magazine/",
    "T Magazine":"section/t-magazine/",
}
NYT_Crawler.site_categories_to_ours={
    "World":"section/world/",
    "U.S.":"section/us/",
    "Politics":"section/politics/",
    "N.Y.":"section/nyregion/",
    "Business":"section/business/",
    "Opinion":"section/opinion/",
    "Tech":"section/technology/",
    "Science":"section/science/",
    "Health":"section/health/",
    "Sports":"section/sports/",
    "Arts":"section/arts/",
    "Books":"section/books/",
    "Style":"section/style/",
    "Food":"section/food/",
    "Travel":"section/travel/",
    "Magazine":"section/magazine/",
    "T Magazine":"section/t-magazine/",
}