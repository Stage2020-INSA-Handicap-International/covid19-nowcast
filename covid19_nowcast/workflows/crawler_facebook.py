from workflow_manager.pipeline import Pipeline
from workflow_manager.step import Step
from workflow_manager.parameter_grid import parameter_grid as PG
import util
import streaming
pipeline=Pipeline(
    [
        Step(
            streaming.collection.crawler_facebook.search,
            params={"query":"https://www.facebook.com/pg/Senegocom/posts/", "count":10, "with_reactions":True},
            name="query",
        )
    ],
    name="crawling")