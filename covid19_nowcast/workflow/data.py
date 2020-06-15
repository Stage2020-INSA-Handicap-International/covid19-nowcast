from datetime import datetime
import pprint
class Data(dict):
    @staticmethod
    def from_dict(parameter_list):
        return Data(parameter_list)

    def to_dict(self, parameter_list):
        return super()

    @staticmethod
    def from_file(parameter_list):
        pass

    def to_file(self, parameter_list):
        pass

    def __init__(self, data={}, generated_through=[], last_modified_at=datetime.now()):
        super().__init__(data)
        self.generated_through = generated_through
        self.last_modified_at = last_modified_at

    def __getitem__(self, key):
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        self.last_modified_at = datetime.now()
        return super().__setitem__(key, value)

    def __repr__(self):
        return "Data(\n\tdata = "+super().__repr__()+", \n\tgenerated_through = "+str(self.generated_through)+", \n\tlast_modified = "+str(self.last_modified_at)+"\n)"
    
    def __str__(self):
        return super().__str__()

    def append_step(self, step):
        self.generated_through.append(step)
        self.last_modified_at = datetime.now()