from workflow.pipeline import Pipeline
from workflow.step import Step
from workflow.parameter_grid import parameter_grid as PG
import util
import streaming
pipeline=Pipeline(
    [
        Step(
            streaming.collection.tweets.crawl_from_raw_query,
            params=PG({"raw_query":["#Sénégal","#Kenya", "#Mali"], "count":[10,50]}),
            name="query",
            export_path="Crawl<query.params[raw_query,count]>",
            outputs=["tweets"]
        )
    ],
    name="crawling")