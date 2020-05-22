import requests
import json
def get_country(countries, **kwargs):
    country_info = [json.loads(requests.get("https://api.covid19api.com/dayone/country/"+country.lower()).text) for country in countries]
    return {"country_covid19":country_info, **kwargs}