from workflow_manager.pipeline import Pipeline
from workflow_manager.step import Step
from workflow_manager.parameter_grid import parameter_grid as PG
import util
import streaming
pipeline=Pipeline(
    [
        Step(
            streaming.collection.tweets.crawl_from_raw_query,
            params=PG({"raw_query":["#Sénégal"], "live":False, "legacy":[True, False], "count":[100]}),
            name="query",
            export_path="Crawl<query.params[raw_query,count]>",
            outputs=["tweets"]
        )
    ],
    name="crawling")