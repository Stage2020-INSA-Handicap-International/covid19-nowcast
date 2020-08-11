import covid19_nowcast.analysis.volume
import covid19_nowcast.analysis.sentiment
import covid19_nowcast.analysis.topics
import covid19_nowcast.analysis.category

from transformers import XLNetForSequenceClassification
from transformers import CamembertForSequenceClassification

from covid19_nowcast.analysis.category import category_classifier
from covid19_nowcast.analysis.sentiment import camemBERTsentiment,xlnetsentiment
from covid19_nowcast.streaming.storage import connect_database
from covid19_nowcast.streaming.storage import tweets
class AnalysisManager():
    sent_clsf={"fr":camemBERTsentiment,"en":xlnetsentiment}
    cat_clsf={"en":category_classifier}
    @staticmethod
    def analyze(data,batch_size):
        data=AnalysisManager.analyse_categories(AnalysisManager.analyse_sentiments(data,batch_size),batch_size)
        tweets.save(data,connect_database())
        return data

    @staticmethod
    def analyse_sentiments(data,batch_size,force=False):
        analyzed_data=[]
        for lang in AnalysisManager.sent_clsf.keys():
            lang_data=[d for d in data if d.get('lang')==lang and ((not force) and d.get("sentiment",None) is None)]
            assert all(d.get("full_text",None) is not None for d in lang_data)
            if lang_data!=[]:
                analyzed_data.extend(AnalysisManager.sent_clsf[lang].predict(lang_data,"full_text",batch_size))
        not_analyzed_data=[d for d in data if not(d.get('lang') in AnalysisManager.sent_clsf.keys() and ((not force) and d.get("sentiment",None) is None))]
        return [*analyzed_data,*not_analyzed_data]

    @staticmethod
    def analyse_categories(data,batch_size,force=False):
        analyzed_data=[]
        for lang in AnalysisManager.cat_clsf.keys():
            lang_data=[d for d in data if d.get('lang')==lang and ((not force) and d.get("category",None) is None)]
            assert all(d.get("full_text",None) is not None for d in lang_data)
            if lang_data!=[]:
                analyzed_data.extend(AnalysisManager.cat_clsf[lang].predict(lang_data,"full_text",batch_size))
        not_analyzed_data=[d for d in data if not(d.get('lang') in AnalysisManager.cat_clsf.keys() and ((not force) and d.get("category",None) is None))]
        return [*analyzed_data,*not_analyzed_data]