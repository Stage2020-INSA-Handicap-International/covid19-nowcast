from workflow_manager.pipeline import Pipeline
from workflow_manager.step import Step
from workflow_manager.parameter_grid import parameter_grid as PG
import util
import streaming
pipeline=Pipeline(
    [
        Step(
            streaming.collection.crawler_facebook.search,
            params=PG({"query":["https://www.facebook.com/pg/Senegocom/posts/","https://www.facebook.com/pg/lafranceaumali/posts/", "https://www.facebook.com/pg/GenerationSenegal/posts/"], "count":20, "with_reactions":True}),
            name="query",
        )
    ],
    name="crawling")