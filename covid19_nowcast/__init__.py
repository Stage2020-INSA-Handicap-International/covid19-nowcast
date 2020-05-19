import json
import sys
from types import ModuleType

import covid19_nowcast.streaming
import covid19_nowcast.analysis
import covid19_nowcast.evaluation
import covid19_nowcast.user_interface

def __main__(workflow_path="workflows/default.json", input_data_path=None, output_data_path=None):
    """
    Entry point for using the covid19-nowcaster
    """
    data={}
    if input_data_path is not None:
        with open(input_data_path, "r") as data_file:
            data = json.loads(data_file.read())

    with open(workflow_path, "r") as workflow:
        workflow=workflow.read()
        workflow=json.loads(workflow)
        for step in workflow:
            params = step.get("params", {})
            data = {**data, **resolve_function(step["function"])(**{**data, **params})}

    if output_data_path is not None:
        with open(output_data_path, "w") as data_file:
            if data is None:
                data = ""
            data_file.write(json.dumps(data))
    return data

def resolve_function(path):
    fragments = path.split(".")
    assert len(fragments)>0

    function = globals().get(fragments[0])
    for fragment in fragments[1:]:
        function = getattr(function, fragment)
    return function