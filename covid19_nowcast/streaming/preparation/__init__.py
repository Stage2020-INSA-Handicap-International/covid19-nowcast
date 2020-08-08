import covid19_nowcast.streaming.preparation.preprocessor

from covid19_nowcast.streaming.preparation.preprocessor import Preprocessor
class PreprocessManager():
    @staticmethod
    def preprocess(data):
        un_processed_data=[d for d in data if d.get("preproc_text",None) is None]
        processed_data=[d for d in data if d.get("preproc_text",None) is not None]
        full_texts=[t["full_text"] for t in un_processed_data]
        if full_texts != []:
            tokens=Preprocessor.preprocess(full_texts)
        un_processed_data=[{**d,"preproc_text":" ".join(tokens[index])} for index,d in enumerate(un_processed_data)]
        data=[*un_processed_data,*processed_data]
        return data