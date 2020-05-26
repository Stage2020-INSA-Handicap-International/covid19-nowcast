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
    Input:
        - workflow_path: path to the file containing instructions to run
        - input_data_path: filepath to a file containing initial data as a Json dictionary for the execution
        - output_data_path: filepath to a file to write output data as a Json dictionary a the end of execution
    Output:
        - data: all entries remaining at the end of execution as a dictionary
    """
    data={}
    if input_data_path is not None:
        with open(input_data_path, "r") as data_file:
            data = json.loads(data_file.read())

    with open(workflow_path, "r") as workflow:
        workflow=workflow.read()
        workflow=json.loads(workflow)
        for command in workflow:
            cmd, instr = list(command.items())[0]
            if cmd == "function":
                data = {**data, **resolve_function(instr)(**data)} # execute function with data and concatenate resulting entries with old data
            elif cmd == "add-params":
                data = {**data, **instr} # concatenate new entries with old data
            elif cmd == "remove-params":
                for src in instr:
                    data.pop(src) # remove entry
            elif cmd == "rename-params":
                for src, dest in instr.items():
                    if data.get(src) is not None:
                        data[dest] = data.pop(src) # replace old entry name with new one

    if output_data_path is not None:
        with open(output_data_path, "w") as data_file:
            if data is None:
                data = ""
            data_file.write(json.dumps(data, indent=4))
    return data

def resolve_function(path):
    fragments = path.split(".")
    assert len(fragments)>0

    function = globals().get(fragments[0])
    for fragment in fragments[1:]:
        function = getattr(function, fragment)
    return function