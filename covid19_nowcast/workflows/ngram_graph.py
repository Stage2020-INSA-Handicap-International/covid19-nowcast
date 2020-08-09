from workflow_manager.pipeline import Pipeline
from workflow_manager.step import Step
from workflow_manager.parameter_grid import parameter_grid as PG
from covid19_nowcast import util
from covid19_nowcast.user_interface import visualisation
pipeline=Pipeline(
    [
        Step(
            util.import_params, 
            params={"filepath":"Datasets/2020_Kenya_preproc.json", "unpack":False},
            outputs=["tweets"],
            read_only_outputs={"tweets"}
        ),
        Step(
            lambda tw:[t["full_text"] for t in tw],
            args=["tweets"],
            outputs=["full_texts"],
            keep_inputs=False
        ),
        Step(
            visualisation.n_gram_graph,
            args=["full_texts"],
            outputs=["graph"],
            keep_inputs=False
        )

    ],
    name="crawling")