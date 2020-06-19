from datetime import datetime
import re 
import copy

class Data(dict):
    @staticmethod
    def rel_deep_copy(data):
        copied_data=Data()
        copied_data.generated_through=copy.deepcopy(data.generated_through)
        for key in data.keys():
            if key not in data.read_only:
                copied_data[key]=copy.deepcopy(data[key])
            else:
                print(key)
                copied_data[key]=data[key]
        return copied_data

    @staticmethod
    def from_dict(parameter_list):
        return Data(parameter_list)

    def to_dict(self):
        return {key:value for key, value in self.items()}

    @staticmethod
    def from_file(parameter_list):
        pass

    def to_file(self, parameter_list):
        pass

    def __init__(self, data={}, generated_through=[], last_modified_at=datetime.now()):
        super().__init__(data)
        self.generated_through = generated_through
        self.last_modified_at = last_modified_at
        self.read_only=set()

    def __getitem__(self, key):
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if type(key) is not str :
            raise TypeError("Data keys must be strings.")
        if key in self.keys() and key in self.read_only:
            raise AttributeError("Attribute "+str(key)+" is read-only.")
        self.last_modified_at = datetime.now()
        return super().__setitem__(key, value)

    def __repr__(self):
        return "Data(\n\tdata = "+super().__repr__()+", \n\tread_only = "+str(self.read_only)+", \n\tgenerated_through = "+str(self.generated_through)+", \n\tlast_modified = \""+str(self.last_modified_at)+"\"\n)"
    
    def __str__(self):
        return super().__str__()

    def append_step(self, step):
        self.generated_through.append(step)
        self.last_modified_at = datetime.now()

    def get_desc_name(self, name_format="</>"):
        final_name=""
        field = re.search(r"<[a-zA-Z0-9_\\.,\[\]/]*>",name_format)
        left, target, right = "","",""
        while field is not None:
            left, target, right =   (
                                    name_format[:field.span()[0]], 
                                    name_format[field.span()[0]+1:field.span()[1]-1], 
                                    name_format[field.span()[1]:]
                                    )
            final_name+=left
            data_str=self.find_data(target)
            final_name+=data_str
            name_format=right
            field = re.search(r"<[a-zA-Z0-9_\\.,\[\]/]*>",name_format)
        final_name+=right
        return final_name
    
    def find_data(self, data):
        """
        data[<keyone>,<keytwo>,<keythree>,...]
        step_name.{function|params[<keyone>,<keytwo>,<keythree>]}
        """
        match=re.search(r"^data\[[,a-zA-Z0-9_]*\]",data)
        if match is not None:
            params_match=re.search(r"\[[a-zA-Z0-9_,]*\]$",data)
            params_names=data[params_match.span()[0]+1:params_match.span()[1]-1]
            params_names=re.split(",",params_names)
            params=[self[param] for param in params_names]
            
            param_formatter=lambda l,r:str(l)+"="+str(r)

            data_str=",".join(list(map(param_formatter,params_names,params)))
        else:
            step_match=re.search(r"^[a-zA-Z0-9_]*\.",data)
            assert step_match is not None
            step_name= data[step_match.span()[0]:step_match.span()[1]-1]
            matching_step=[step for step in self.generated_through if step.name==step_name]
            assert len(matching_step)==1
            matching_step=matching_step[0]

            function_match=re.search(r"\.[a-zA-Z0-9_]*$",data)
            if function_match is not None:
                data_str=matching_step.function[0].__name__
            else:
                params_match=re.search(r"\.params\[[a-zA-Z0-9_,]*\]$",data)
                assert params_match is not None
                params_match=re.search(r"\[[a-zA-Z0-9_,]*\]$",data)
                params_names=data[params_match.span()[0]+1:params_match.span()[1]-1]
                params_names=re.split(",",params_names)
                params=[matching_step.params[param] for param in params_names]
                
                param_formatter=lambda l,r:str(l)+"="+str(r)

                data_str=",".join(list(map(param_formatter,params_names,params)))
        return data_str