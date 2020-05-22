def user_count(tweets, analysis={}, **kwargs):
    user_set={tweet["user"]["id_str"] for tweet in tweets}
    analysis["user_count"]=len(user_set)
    return {"analysis":analysis}

from datetime import datetime
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
from collections import Counter
def tweets_per_day(tweets, analysis={}, **kwargs):
    date_set=Counter(datetime.date(datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S %z %Y')) for tweet in tweets)
    analysis["tweets_per_day"]=date_set
    return {"analysis":analysis}

def tweets_per_country(tweets, analysis={}, **kwargs):
    date_set=Counter( tweet["user"].get("derived", {"locations":[{"country_code":"N/A"}]}).get("locations", [{"country_code":"N/A"}])[0]["country_code"] for tweet in tweets)
    analysis["tweets_per_country"]=date_set
    return {"analysis":analysis}

def tweets_per_country_normalised_on_pop(tweets, countries, analysis={}, **kwargs):
    date_set=Counter( tweet["user"].get("derived", {"locations":[{"country_code":"N/A"}]}).get("locations", [{"country_code":"N/A"}])[0]["country_code"] for tweet in tweets)
    date_set= {**{date:count/[country[0]["population"] for country in countries if country[0]["alpha3Code"]==date][0] for date, count in date_set.items() if date != "N/A"}, **{ date:count for date, count in date_set.items() if date == "N/A"}}
    analysis["tweets_per_country"]=date_set
    return {"analysis":analysis}