from workflow_manager.pipeline import Pipeline
from workflow_manager.step import Step
from workflow_manager.parameter_grid import parameter_grid as PG
import util
import streaming
pipeline=Pipeline(
    [
        Step(
            streaming.collection.tweets.crawl_from_raw_query,
            params=PG({"raw_query":["India AND (corona OR coronavirus OR virus OR covid-19 OR covid19)"], "live":[False], "legacy":[False], "count":[1000]}),
            name="query",
            export_path="Crawl<query.params[raw_query,count]>",
            outputs=["tweets"]
        )
    ],
    name="crawling")