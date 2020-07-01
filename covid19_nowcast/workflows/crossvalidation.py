from workflow_manager.pipeline import Pipeline
from workflow_manager.step import Step
from workflow_manager.metastep import MetaStep

from workflow_manager.parameter_grid import parameter_grid as PG
import util
from workflow import meta

from sklearn.model_selection import cross_validate
from sklearn.metrics import recall_score
import numpy as np
pipeline=Pipeline([
                Step(
                    cross_validate,
                    args=["classifier","samples","labels"],
                    params={"scoring":['precision_macro', 'recall_macro', 'f1_macro'], "cv":3, "verbose":10, "n_jobs":-1, "return_train_score":True},
                    outputs=["scores"]
                ),
                Step(
                    lambda sc:np.average(sc["test_f1_macro"]),
                    args=["scores"],
                    outputs=["summary"]
                ),
                MetaStep(  
                    meta.top_N,
                    params={"n_best":5, "criterion":lambda data:data["summary"]}
                ),
                Step(
                    print,
                    args=["summary", "vectorizing_params"]
                ),
                Step(
                    util.remove_params,
                    args=["labels", "samples","classifier"],
                    keep_inputs=False
                ),
            ],name="cross_validation")