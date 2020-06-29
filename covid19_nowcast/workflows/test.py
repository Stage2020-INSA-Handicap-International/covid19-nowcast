from workflow.pipeline import Pipeline
from workflow.step import Step
from workflow.parameter_grid import parameter_grid as PG
import util
import analysis
pipeline=Pipeline([
            Step(
                util.import_params, 
                params={"filepath":"../Datasets/2020_Kenya_preprocDict.json", "unpack":True},
                outputs=["test_tweets"]
            ),
            Step(
                lambda x: [tweet["full_text"] for tweet in x],
                args=["test_tweets"],
                outputs=["preproc_texts"]
            ),
            Step(
                analysis.sentiment.classify, 
                args=["classifier","preproc_texts"],
                outputs=["labels"],
                keep_inputs=True,
                #export_path="./output/labels_<classifier.function>"
            ),
            Step(
                analysis.sentiment.classify, 
                args=["classifier","preproc_texts"],
                outputs=["sentiment_proba"],
                params={"return_type":"proba"},
                keep_inputs=False,
                #export_path="./output/labels_<classifier.function>"
            ),
            ],name="test_sentiment")