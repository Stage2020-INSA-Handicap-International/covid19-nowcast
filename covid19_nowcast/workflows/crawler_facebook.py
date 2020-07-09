from workflow_manager.pipeline import Pipeline
from workflow_manager.step import Step
from workflow_manager.parameter_grid import parameter_grid as PG
import util
import streaming
pipeline=Pipeline(
    [
        Step(
            streaming.collection.crawler_facebook.search,
            params=PG({"query":["https://www.facebook.com/pg/EstoySad19/posts/"], "count":5, "with_reactions":True}),
            outputs=["posts"],
            name="query",
        )
    ],
    name="crawling")#,"https://www.facebook.com/pg/Senegocom/posts/"