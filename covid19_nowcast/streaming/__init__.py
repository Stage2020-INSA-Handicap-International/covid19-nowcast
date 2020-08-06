import covid19_nowcast.streaming.collection
import covid19_nowcast.streaming.storage
import covid19_nowcast.streaming.preparation
import covid19_nowcast.streaming.models

from covid19_nowcast.streaming.collection import collect_twitter_data

class TimeSubset():
    pass

class CollectionManager():
    @staticmethod
    def collect_sts_data(country,source,lang,date_from,date_to):
        data=None
        if source=="twitter":
            data=collect_twitter_data(country,lang,date_from,date_to)
        return data

    @staticmethod
    def determine_missing_time_subsets(country,source,lang,date_from,date_to):
        return None