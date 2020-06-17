from workflow.data import Data
import inspect
import types
import copy
import datetime
import util
import itertools
class Step():

    def __init__(self, function, args=None, nargs=None, outputs=None, params=[{}], keep_inputs=True, name="Step", export_path=None):
        super().__init__()

        assert function is not None and (callable(function) or type(function) is list)
        if type(function) is list:
            self.function = function
        else:
            self.function = [function]

        assert type(name) is str
        self.name=name

        self.args=[]
        if args is not None:
            if type(self.args) is str:
                self.args.append(args)
            else:
                assert type(self.args) is list or type(self.args) is tuple
                for input_key in args:
                    assert type(input_key) is str
                self.args.extend(args)

        self.nargs={}
        if nargs is not None:
            assert type(self.nargs) is set
            for input_key in nargs:
                assert type(input_key) is str
            self.args.extend(nargs)

        self.outputs=None
        if outputs is not None:
            self.outputs=[]
            if type(outputs) is str:
                self.outputs.append(outputs)
            else:
                assert type(outputs) is list or type(outputs) is tuple
                for input_key in outputs:
                    assert type(input_key) is str
                self.outputs.extend(outputs)

        assert type(params) is dict or type(params) is list or isinstance(params, types.GeneratorType)
        if type(params) is dict:
            self.params=[params]
        else:
            self.params=params
        assert type(keep_inputs) is bool
        self.keep_inputs=keep_inputs

        assert export_path is None or type(export_path) is str
        self.export_path = export_path

    def run(self, data_containers):
        print(self)
        # Collecting input values from container
        variants_containers=[]
        for data_container in data_containers:
            args=[]
            for input_key in self.args:
                args.append(data_container[input_key])

            nargs={}
            for input_key in self.nargs:
                nargs[input_key]=data_container[input_key]
            
            backup_params=self.params
            if isinstance(self.params, types.GeneratorType) or isinstance(self.params,itertools._tee):
                self.params, backup_params = itertools.tee(self.params)

            for param_variant in self.params:
                variant_container=copy.deepcopy(data_container)
                for param_key in param_variant:
                    nargs[param_key]=param_variant[param_key]
                # Running function and collecting outputs
                for funct in self.function:
                    funct_container=variant_container
                    if len(self.function)>1:
                        funct_container=copy.deepcopy(variant_container)
                    
                    output = funct(*args, **nargs)

                    if not self.keep_inputs:
                        for input_key in self.args:
                            del funct_container[input_key]
                        for input_key in self.nargs:
                            del funct_container[input_key]

                    if self.outputs is not None:
                        # Storing outputs in container
                        if type(output) is tuple:
                            assert len(output) == len(self.outputs)
                        elif output is not None:
                            assert len(self.outputs)==1
                            output=[output]

                        for index, output_key  in enumerate(self.outputs):
                            funct_container[output_key]=output[index]
 
                    # Log the specific step infos in Data container
                    mem_params=self.params
                    mem_functs=self.function
                    self.params=param_variant
                    if isinstance(funct, types.LambdaType) and funct.__name__ == "<lambda>":
                        self.function=[util.lambda_function]
                    else:
                        self.function=[funct]
                    step_variant=copy.deepcopy(self)
                    self.params=mem_params
                    self.function=mem_functs
                    funct_container.append_step(step_variant)

                    if self.export_path is not None:
                        path=funct_container.get_desc_name(self.export_path)
                        util.export_param(funct_container.to_dict(),path)
                        util.export_param(funct_container.to_dict(),path, pickle=True)
                    variants_containers.append(funct_container)

                #generator is exhausted => resuscitate it
                self.params=backup_params
        data_containers=variants_containers
        return data_containers

    def __repr__(self):
        return "Step(function = "+str([funct.__name__ for funct in self.function])+", args = "+ str(self.args) + ", nargs = " + str(self.nargs) + ", outputs = "+ str(self.outputs) + ", params = " + str(self.params) + ", keep_inputs = "+str(self.keep_inputs)+", name = "+self.name+")"