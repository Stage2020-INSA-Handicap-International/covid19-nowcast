# Workflow imports
from workflow_manager.pipeline import Pipeline
from workflow_manager.step import Step
from workflow_manager.parameter_grid import parameter_grid as PG

# Subpipelines imports
from workflows.train import pipeline as train_pipe
from workflows.test import pipeline as test_pipe

pipeline = Pipeline([
    train_pipe,
    test_pipe
])