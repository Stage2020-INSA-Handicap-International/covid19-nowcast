from workflow.step import Step

import copy
class Pipeline():
    def __init__(self, steps=[], name="Pipeline"):
        super().__init__()

        self.name=name

        assert Pipeline.check_instance_types(steps)
        self.steps=steps

    def run(self,data_containers):
        for step in self.steps:
            if type(step) is list:
                data_variants = [step_variant.run(copy.deepcopy(data_containers)) for step_variant in step] # deepcopy for different subworkflow dataspaces

                # Flatten containers lists created by variants
                data_containers=[]
                for data_variant in data_variants:
                    data_containers.extend(data_variant)
            else:
                data_containers=step.run(data_containers) # if there is only one receiver step, then it is not necessary to deepcopy
        return data_containers

    @staticmethod
    def check_instance_types(step, recursive=True):
        return isinstance(step, Step) \
            or isinstance(step, Pipeline) \
            or (type(step) is list \
                and all([Pipeline.check_instance_types(substep) for substep in step]))
