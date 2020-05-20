

def search_from_terms(api, terms, **kwargs):
    tweets=api.GetSearch(term=terms)
    return tweets

def search_from_geocode(api, geocode, **kwargs):
    tweets=api.GetSearch(geocode=geocode)
    return tweets

def search_from_raw_query(api, raw_query, **kwargs):
    tweets=api.GetSearch(raw_query=raw_query)
    return tweets