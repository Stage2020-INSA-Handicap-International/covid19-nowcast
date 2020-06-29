from workflow.pipeline import Pipeline
from workflow.step import Step
from workflow.parameter_grid import parameter_grid as PG
import util
import analysis
pipeline=Pipeline([
            Step(
                util.import_params, 
                params={"filepath":"output/sentV20.json", "unpack":True},
                outputs=["labeled_tweets"]
            ),
            Step(
                lambda tw:[t for t in tw if t["final_sentiment"]=="positive" and t["sentiment"]=="positive" and t["sentiment_proba"]==0.4],
                args=["labeled_tweets"],
                outputs=["filtered_tweets"],
                keep_inputs=False,
            ),
            ],name="selector")