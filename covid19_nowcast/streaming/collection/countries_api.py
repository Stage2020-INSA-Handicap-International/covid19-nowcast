import requests
import json
def get_countries(countries, **kwargs):
    countries_info = [json.loads(requests.get("https://restcountries.eu/rest/v2/name/"+country.lower()).text) for country in countries]
    return {"countries":countries_info, **kwargs}