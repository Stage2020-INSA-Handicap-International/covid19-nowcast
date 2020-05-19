

def search_from_terms(api, terms, since_id=None, max_id=None, until=None, since=None, count=15, lang=None, locale=None, result_type='mixed', include_entities=None, return_json=False):
    tweets=api.GetSearch(term=terms)
    return tweets

def search_from_geocode(api, geocode, since_id=None, max_id=None, until=None, since=None, count=15, lang=None, locale=None, result_type='mixed', include_entities=None, return_json=False):
    tweets=api.GetSearch(geocode=geocode)
    return tweets

def search_from_raw_query(api, raw_query, since_id=None, max_id=None, until=None, since=None, count=15, lang=None, locale=None, result_type='mixed', include_entities=None, return_json=False):
    tweets=api.GetSearch(raw_query=raw_query)
    return tweets