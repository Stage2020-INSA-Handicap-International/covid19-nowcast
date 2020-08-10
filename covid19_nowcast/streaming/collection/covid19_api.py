import requests
import json
from datetime import datetime
from covid19_nowcast import util
def get_countries_info(countries, date_from, date_to, entries = ["Date", "Confirmed", "Deaths", "Recovered", "Active"]):
    """
    Searches api.covid19api.com for COVID-19 cases
    Input:
        - countries: a list of full country names corresponding to those required by the api.
        - entries : subset of available entries in the api's response
            Available entry keys are in ["Date", "Confirmed", "Deaths", "Recovered", "Active", "Date", "Country", "Province", "City", "CountryCode", "Lat", "Lon"]
    Output:
        - countries_covid19: an entry to a dictionary containing entries named after all elements of *countries*, which each contain a dictionary containing all correponding keys:info in *entries* 
    """
    country_info = {country:json.loads(requests.get("https://api.covid19api.com/country/{}?from={}&to={}".format(country.lower(),date_from,date_to)).text) for country in countries}
    for country in country_info.values():
        for situation in country:
            situation["Date"]= datetime.strftime(datetime.date(datetime.strptime(situation["Date"], '%Y-%m-%dT%H:%M:%SZ')),'%Y-%m-%dT00:00:00Z')
            situation = util.filter_keys(situation,entries)
    return country_info

def get_countries():
    """
    Searches available countries in api.covid19api.com 
    Input:
        - N/A
    Output:
        - a list of dictionaries containing the "Country" (name), "Slug" (used in API requests) and "ISO2" (abbreviation) for each available country
    """
    countries = json.loads(requests.get("https://api.covid19api.com/countries").text) 
    return countries