import json
import sys
from types import ModuleType
import copy
import importlib

import streaming
import analysis
import evaluation
import user_interface
import workflow
import workflows
import util
from workflow.data import Data
def run_workflow(workflow="workflows.test_workflow", input_data_path=None, output_data_path=None):
    """

    """
    data=[Data({})]
    if input_data_path is not None:
        with open(input_data_path, "r") as data_file:
            data = eval(data_file.read())
        
    module = importlib.import_module(workflow)
    data=module.pipeline.run(data)

    if output_data_path is not None:
        with open(output_data_path, "w") as data_file:
            data_file.write(str(data))
    return data

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("-wf", "--workflow", dest="workflow", type=str, default="workflows.test_workflow",
                        help="import workflow with Python syntax", metavar="import.path")
    parser.add_argument("-i", "--input-data", dest="input_data_path", type=str,
                        help="filepath to read initial data", metavar="filepath")
    parser.add_argument("-o", "--output-data", dest="output_data_path", type=str,
                        help="filepath to write execution data", metavar="filepath")

    args = parser.parse_args()
    run_workflow(args.workflow, args.input_data_path, args.output_data_path)