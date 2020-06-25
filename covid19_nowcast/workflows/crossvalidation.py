from workflow.pipeline import Pipeline
from workflow.step import Step
from workflow.parameter_grid import parameter_grid as PG
import util

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
                Step(
                    print,
                    args=["summary"]
                ),
                Step(
                util.remove_params,
                args=["labels", "classifier"],
                keep_inputs=False
            )
            ],name="cross_validation")