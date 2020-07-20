from workflow_manager.pipeline import Pipeline
from workflow_manager.step import Step
from workflow_manager.parameter_grid import parameter_grid as PG
import util
import analysis
from streaming.preparation.preprocessor import Preprocessor
pipeline=Pipeline([
            Step(
                util.import_params, 
                params={"filepath":"output/tweets_india0.json", "unpack":True},
                outputs=["tweets"]
            ),
            Step(
                lambda tweets:[t["full_text"] for t in tweets],
                args=["tweets"],
                outputs=["full_texts"]
            ),
            Step(
                Preprocessor.preprocess,
                args=["full_texts"],
                outputs=["preproc_list"],
                keep_inputs=False
            ),
            Step(
                lambda prep, tw:[{**t, "sentiment":"N/A","preproc_text":" ".join(prep[index])} for index, t in enumerate(tw)],
                args=["preproc_list","tweets"],
                outputs=["tweets"],
                keep_inputs=False
            ),
            ],name="preprocessor")