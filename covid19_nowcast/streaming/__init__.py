import covid19_nowcast.streaming.collection
import covid19_nowcast.streaming.storage
import covid19_nowcast.streaming.preparation
import covid19_nowcast.streaming.models

from covid19_nowcast.streaming.collection import collect_twitter_data
from covid19_nowcast.streaming.collection import hydrate
from covid19_nowcast.streaming.storage import DBTimeSubset
import progressbar
from covid19_nowcast import util

class CollectionManager():
    @staticmethod
    def collect_sts_data(country,source,lang,date_from,date_to):

        data=None
        db_time_subsets=DBTimeSubset(country["ISO2"],source,lang)
        present_subsets,missing_subsets=db_time_subsets.subsets_status(date_from,date_to)
        print("Missing subsets:",missing_subsets)
        data=[]
        if source=="twitter":
            data.extend(db_time_subsets.get_data(present_subsets))
            # hydrated_data=[]
            # for i in range(0,len(data),100):
            #     hydrated_data.extend(hydrate(data[i:min(i+100,len(data))]))
            # data=hydrated_data
        if missing_subsets.intervals != []:
            with progressbar.ProgressBar(max_value=len(missing_subsets.intervals), prefix="Missing subsets: ") as bar:
                i=0
                bar.update(i)
                for date_from,date_to in missing_subsets.to_tuples():
                    if source=="twitter":
                        data.extend(collect_twitter_data(country,lang,date_from,date_to))
                    i+=1
                    bar.update(i)
        data=db_time_subsets.insert_data(data,missing_subsets)

        #data=util.import_params("covid19_nowcast/util/2020_tweets.json")
        return data
