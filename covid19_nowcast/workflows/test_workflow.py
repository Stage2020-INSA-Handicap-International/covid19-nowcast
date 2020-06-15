from workflow.pipeline import Pipeline
from workflow.step import Step
from workflow.parameter_grid import parameter_grid as PG

import util
from streaming import collection
pipeline=Pipeline([
    [
        Step(util.add_params,params=[
                {"query":"#Mali", "count":1},
                {"query":"#Kenya", "count":2}
            ], 
            outputs=["query", "count"]),
        Step(util.add_params,
            params=PG({
                "query":["#Sénégal","#COVID-19"], 
                "count":range(10,20,5)
            }), 
            outputs=["query", "count"])
    ],
    Step(collection.tweets.crawl_from_raw_query,args=["query", "count"],outputs="tweets")
    ])