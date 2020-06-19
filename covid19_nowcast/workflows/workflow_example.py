# Workflow imports
from workflow.pipeline import Pipeline
from workflow.step import Step
from workflow.parameter_grid import parameter_grid as PG

# Functions imports
import util
from streaming import collection

pipeline=Pipeline([ # A list of steps or sub-pipelines to be run in sequence

        [   # Alternate workflows are possible by supplying a list of step variants
            Step(util.add_params, # A list of functions can also be supplied if they are to have the same parameters/interface
                params=[ 
                    # A step can receive either a single dictionary, or a list of dictionary. 
                    # In the latter case, it creates separate variant executions
                    {"query":"#Mali", "count":1},
                    {"query":"#Kenya", "count":2}
                ], 
                outputs=["query", "count"]),
            Step(util.add_params,
                params=PG({ 
                    # A matrix of params can be generated with a PG initiated with a dictionary of iterables.
                    # Some keys may be non iterable.
                    # Values which are by nature iterable should be put in a list to avoid being interated on (e.g. strings)
                    "query":["#Sénégal","#COVID-19"], 
                    "count":range(10,20,5)
                }), 
                outputs=["query", "count"])
        ],
        Step(collection.tweets.crawl_from_raw_query,args=["query", "count"],outputs="tweets")
    ])