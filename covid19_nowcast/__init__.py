import json
import sys
from types import ModuleType
import copy

import covid19_nowcast.streaming
import covid19_nowcast.analysis
import covid19_nowcast.evaluation
import covid19_nowcast.user_interface
from covid19_nowcast import util

def __main__(workflow_path="workflows/default.json", workflow_list=None, data={}, input_data_path=None, output_data_path=None):
    """
    Entry point for using the covid19-nowcaster
    Input:
        - workflow_path: path to the file containing instructions to run
        - input_data_path: filepath to a file containing initial data as a Json dictionary for the execution
        - output_data_path: filepath to a file to write output data as a Json dictionary a the end of execution
    Output:
        - data: all entries remaining at the end of execution as a dictionary
    """
    #data=copy.deepcopy(data)

    if input_data_path is not None:
        with open(input_data_path, "r") as data_file:
            data = json.loads(data_file.read())
            
    if workflow_list is None:
        with open(workflow_path, "r") as workflow:
            workflow_list=workflow.read()
            workflow_list=json.loads(workflow_list)
    
    for command in workflow_list:
        cmd, instr = list(command.items())[0]
        if cmd == "workflow":
            """
            Runs a sub-workflow.
            This workflow is either explicitly written in the original .json as a list of commands, or is imported from another .json file.
            Keys:
                - params: (opt) a list of parameters in *data* which should be visible to the subworkflow;
                - path: (alt with *instructions*) a string filepath to the .json workflow to run;
                - instructions: (alt with *path*) a list of commands following the same structure as that of a workflow
            Structure:  {
                "workflow":{
                    # optional: if params is not present, all parameters in data will be inputted
                    "params":["paramToInputInWorkflow", "Another", "YetAnother"],

                    "path":"path_to_sub_workflow.json"
                    # or
                    "instructions":[{ "function":"example" },{...},...]
                }
            }
            """
            params=instr.get("params", list(data.keys()))
            sub_data={param:data["params"] for param in params}
            if instr.get("path"):
                data={**data,**__main__(workflow_path=instr["path"], data=sub_data)}
            else:
                data={**data,**__main__(workflow_list=instr["instructions"], data=sub_data)}
        elif cmd == "function":
            """
            Executes a function with available variables in data.
            For the function to run properly, it will require that all named and required parameters are in *data*, 
            meaning that these variables were defined beforehand during execution.
            Structure:
            {
                "function":"covid19_nowcast.path.to.function"
            }
            """
            data = {**data, **resolve_function(instr)(**data)} # execute function with data and concatenate resulting entries with old data
        elif cmd == "add-params":
            data = {**data, **instr} # concatenate new entries with old data
            """
            Adds parameter variables to the current data which will become usable for functions.
            This data should be in .json format.
            Structure:
            {
                "add-params":{
                    "aList":["My", "imagination"],
                    "aString":"knows",
                    "aDict":{"no":"bounds"}
                }
            }
            """
        elif cmd == "remove-params":
            """
            Removes parameter variables from the current data.
            Structure:
            {
                "remove-params":["Entries","to", "Remove"]
            }
            """
            for src in instr:
                data.pop(src) # remove entry
        elif cmd == "filter-params":
            """
            Keeps or removes given parameters depending of the value of "keep" entry.
            Keys:
                - "params": a list of keys to keep or remove.
                - "keep": (opt) a boolean to determine whether to keep or delete *params*
            Structure:
            {
                "filter-params":{
                    "params":["some", "params"],
                    # optional: if keep is absent, the default value is to keep the parameters in *params* 
                    "keep":true
                }
            }
            """
            data=util.filter_keys(data,instr["params"], instr.get("keep", True))
        elif cmd == "rename-params":
            """
            Renames parameter variables from the current data.
            Structure:
            {
                "rename-params":{
                    "Ntries":"Entries", 
                    "two":"to",
                    "Renamme":"rename"
                }
            }
            """
            for src, dest in instr.items():
                if data.get(src) is not None:
                    data[dest] = data.pop(src) # replace old entry name with new one
        elif cmd == "import-params":
            """
            Imports parameter variables from a file.
            Keys:
                - "path": Filepath to the data.
                - "dst": (opt) a string name for the key which will contain the input data.
            Structure:
            {
                "import-params":{
                    "path":"filepath", 
                    # optional: if *dst* is absent, each imported object will be added directly into *data*. 
                    #           In that case, all objects shall be already in a dictionary in the input file.
                    "dst":"name_of_dictionary_key",
                }
            }
            """
            path=instr["path"]

            into=None
            with open(path, "r") as file:
                into=eval(file.read())

            dst=instr.get("dst")
            if dst is not None:
                data[dst]=into
            else:
                data={**data, **into}

        elif cmd == "export-params":
            """
            Exports some parameters into a file in Json format
            Keys:
                - "path": path to the file;
                - "params": (opt) params to export, if absent, all will be exported.
            Structure:
            {
                "export-params":{
                    "path":"filepath",
                    # optional
                    "params":["Those", "keys_values", "will", "be", "exported"]
                }
            }
            """
            path=instr.get("path")
            params=instr.get("params", data.keys())
            try:
                with open(path,"w") as file:
                    json.dump({param:data[param] for param in params}, file, indent=4)
            except TypeError:
                raise(TypeError("Path should be a string and Params a list of strings"))
            except KeyError:
                raise(TypeError("Queried parameter is not currently in the data"))

        elif cmd == "pack-params":
            """
            Puts objects into a common dictionary.
            Keys:
                - "params": parameters to put in a dictionary
                - "dst": key-name of that dictionary which will be added to *data*
            Structure:
            {
                "pack-params":{
                    "params":["Pack", "those", "parameters"],
                    "dst":"common_dict_key" 
                }
            }
            For example with data={"Tweets":[...], "labels":[...], "some_other_parameters":...}
            "pack-params":{"params":["Tweets", "labels"], "dst":"labeled_tweets"}
            will create {"labeled_tweets":{"Tweets":[...], "labels":[...]}} in *data*
            """
            params=instr["params"]
            dst=instr["dst"]
            data={**data, **{dst:{param:data[param] for param in params}}}
            
        elif cmd == "unpack-params":
            """
            Takes values out of a common dictionary.
            Keys:
                - "params": parameters to move out of a dictionary
                - "src": key-name of that dictionary present in *data*
            Structure:
            {
                "unpack-params":{
                    "params":["Unpack", "those", "parameters"],
                    "src":"common_dict_key" 
                }
            }
            For example with data={"labeled_tweets":{"Tweets":[...], "labels":[...]}}
            "unpack-params":{"params":["Tweets", "labels"], "src":"labeled_tweets"}
            will add "Tweets":[...] and "labels":[...] in *data*
            """
            src=instr["src"]
            params=instr.get("params", src.keys())
            data={**data, **{param:src[param] for param in params}}
            
        elif cmd == "display-params":
            """
            Displays some parameters in *data*.
            Structure:{
                "display-params":["Values","to","display"]
            }
            """
            if instr == {}:
                print(data)
            else:
                for param in instr:
                    print(data[param])
        
        elif cmd == "display-entries":
            """
            Displays all keys in *data*.
            Structure:{
                "display-entries":{}
            }
            """
            print(data.keys())
        elif cmd == "pause":
            """
            Pauses the workflow.
            Structure:{
                "pause":{}
            }
            """
            input("Wainting for input to continue")

    if output_data_path is not None:
        with open(output_data_path, "w") as data_file:
            if data is None:
                data = ""
            json.dump(data, data_file, indent=4)
    return data

def resolve_function(path):
    fragments = path.split(".")
    assert len(fragments)>0

    function = globals().get(fragments[0])
    for fragment in fragments[1:]:
        function = getattr(function, fragment)
    return function