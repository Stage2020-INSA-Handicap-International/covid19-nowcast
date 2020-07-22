class Crawler():
    def __init__(self, root_url,categories_to_crawl,site_categories_to_ours,parsed_urls=[]):
        self.root_url=root_url
        self.categories_to_crawl=categories_to_crawl
        self.site_categories_to_ours=site_categories_to_ours
        self.parsed_urls=parsed_urls

    def crawl(self, count):
        return self.articles_from_site(self.root_url)

    def articles_from_site(self, link):
        raise NotImplementedError

    def articles_from_category(self, link):
        raise NotImplementedError

    def parse_article(self, link):
        raise NotImplementedError