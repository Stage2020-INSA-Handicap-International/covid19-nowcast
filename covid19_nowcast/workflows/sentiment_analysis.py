from workflow_manager.pipeline import Pipeline
from workflow_manager.step import Step
from workflow_manager.parameter_grid import parameter_grid as PG
import util
import analysis
pipeline=Pipeline([
            Step(
                util.import_params, 
                params={"filepath":"../Datasets/preprocLabeledDict1p6M.json", "unpack":True},
                outputs=["tweets","labels"]
            ),
            Step([analysis.sentiment.train_MNB_classifier,analysis.sentiment.train_SVM_classifier], 
                args=["tweets", "labels"], 
                outputs=["classifier"],
                name="classifier"
            ),
            Step(
                analysis.sentiment.get_coeffs,
                args=["classifier"],
                outputs=["coeffs"],
                export_path="./output/coeffs_<classifier.function>"
            ),
            Step(
                util.import_params, 
                params={"filepath":"../Datasets/2020_Kenya_preprocDict.json", "unpack":True},
                outputs=["test_tweets"]
            ),
            Step(
                lambda x: [tweet["full_text"] for tweet in x],
                args=["test_tweets"],
                outputs=["full_texts"]
            ),
            Step(
                analysis.sentiment.classify, 
                args=["classifier","full_texts"],
                outputs=["labels"],
                keep_inputs=False,
                export_path="./output/labels_<classifier.function>"
            ),
            ],name="sentiment_analysis")