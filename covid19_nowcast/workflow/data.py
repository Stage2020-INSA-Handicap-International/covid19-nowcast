from datetime import datetime

class Data(dict):
    @staticmethod
    def from_dict(parameter_list):
        pass

    def to_dict(self, parameter_list):
        return super()

    @staticmethod
    def from_file(parameter_list):
        pass

    def to_file(self, parameter_list):
        pass

    def __init__(self, iterable):
        super().__init__(iterable)
        self.generated_through = []
        self.last_modified_at = datetime.now()

    def __getitem__(self, key):
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        self.last_modified_at = datetime.now()
        return super().__setitem__(key, value)

    def __repr__(self):
        return super().__repr__()
    
    def __str__(self):
        return super().__str__()

    def append_step(self, step):
        self.generated_through.append(step)
        self.last_modified_at = datetime.now()