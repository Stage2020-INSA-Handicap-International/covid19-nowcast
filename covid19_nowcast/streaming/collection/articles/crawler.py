class Crawler():
    def __init__(self, root_url,categories_to_crawl,site_categories_to_ours,HI_category_nomenclature=False,parsed_urls=[]):
        self.root_url=root_url
        self.site_categories_to_ours=site_categories_to_ours
        self.parsed_urls=parsed_urls
        if HI_category_nomenclature:
            self.categories_to_crawl=self.our_categories_to_theirs(categories_to_crawl)
        else:
            self.categories_to_crawl=categories_to_crawl

    def crawl(self, count):
        return [a for a in self.articles_from_site(self.root_url) if a is not None]

    def articles_from_site(self, link):
        raise NotImplementedError

    def articles_from_category(self, link):
        raise NotImplementedError

    def parse_article(self, link):
        raise NotImplementedError

    def our_categories_to_theirs(self,our_cats_list):
        their_cats_list=[key for key, value in self.site_categories_to_ours.items() if value in our_cats_list]
        return their_cats_list