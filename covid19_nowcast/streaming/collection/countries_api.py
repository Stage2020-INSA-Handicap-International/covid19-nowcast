import requests
import json
from covid19_nowcast import util
def get_countries(countries, entries = ["alpha3Code", "name"], **kwargs):
    """
    Searches restcountries.eu for country infos
    Input:
        - countries: a list of full country names corresponding to those required by the api.
        - entries : subset of available entries in the api's response
            Available entry keys are in ["name", "topLevelDomain", "alpha2Code", "alpha3Code", "callingCodes", "capital",
                                        "altSpellings", "region", "subregion", "population", latlng", "demonym", "area", 
                                        "gini", timezones", "borders", "nativeName", "numericCode", "currencies", "languages", 
                                        "translations", "flag", "regionalBlocs", "otherAcronyms", "otherNames", "cioc"]
    Output:
        - countries_info: an entry to a dictionary containing entries named after all elements of *countries*, which each contain a dictionary containing all correponding keys:info in *entries* 
    """
    countries_info = {country:json.loads(requests.get("https://restcountries.eu/rest/v2/name/"+country.lower()).text)[0] for country in countries}
    for country in countries_info.values():
        country = util.filter_keys(country,entries)

    return {"countries_info":countries_info}