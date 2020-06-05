from workflow.data import Data
import inspect
import types
import copy

class Step():

    def __init__(self, function, args=None, nargs=None, outputs=None, params=[{}], keep_inputs=True):
        super().__init__()

        assert function is not None and callable(function)
        self.name=function.__name__
        self.function = function

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

        self.outputs=[]
        if outputs is not None:
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

    def run(self, data_containers):
        print(data_containers)
        # Collecting input values from container
        variants_containers=[]
        for data_container in data_containers:
            args=[]
            for input_key in self.args:
                args.append(data_container[input_key])

            nargs={}
            for input_key in self.nargs:
                nargs[input_key]=data_container[input_key]

            for param_variant in self.params:
                variant_container=copy.deepcopy(data_container)
                for param_key in param_variant:
                    nargs[param_key]=param_variant[param_key]
                # Running function and collecting outputs
                output= self.function(*args, **nargs)

                # Storing outputs in container
                if type(output) is tuple:
                    assert len(output) == len(self.outputs)
                    for index, output_key  in enumerate(self.outputs):
                        variant_container[output_key]=output[index]
                else:
                    assert len(self.outputs)==1
                    variant_container[self.outputs[0]]=output

                if not self.keep_inputs:
                    for input_key in self.args:
                        del variant_container[input_key]
                    for input_key in self.nargs:
                        del variant_container[input_key]

                # Log the specific step infos in Data container
                mem_params=self.params
                self.params=param_variant
                step_variant=copy.deepcopy(self)
                self.params=mem_params
                variant_container.append_step(step_variant)

                variants_containers.append(variant_container)

        data_containers=variants_containers
        return data_containers
