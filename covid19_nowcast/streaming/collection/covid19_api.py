import requests
import json
from datetime import datetime
import util
def get_countries_info(countries, entries = ["Date", "Confirmed", "Deaths", "Recovered", "Active"], **kwargs):
    """
    Searches api.covid19api.com for COVID-19 cases
    Input:
        - countries: a list of full country names corresponding to those required by the api.
        - entries : subset of available entries in the api's response
            Available entry keys are in ["Date", "Confirmed", "Deaths", "Recovered", "Active", "Date", "Country", "Province", "City", "CountryCode", "Lat", "Lon"]
    Output:
        - countries_covid19: an entry to a dictionary containing entries named after all elements of *countries*, which each contain a dictionary containing all correponding keys:info in *entries* 
    """
    country_info = {country:json.loads(requests.get("https://api.covid19api.com/dayone/country/"+country.lower()).text) for country in countries}
    for country in country_info.values():
        for situation in country:
            situation["Date"]= datetime.strftime(datetime.date(datetime.strptime(situation["Date"], '%Y-%m-%dT%H:%M:%SZ')),'%b %d %Y')
            situation = util.filter_keys(situation,entries)
    return country_info