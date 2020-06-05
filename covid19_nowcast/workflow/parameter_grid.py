import copy

def iterable(obj):
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True

def parameter_grid(dictionary, remaining_keys=None):
    if remaining_keys is None:
        print("i")
        remaining_keys=list(dictionary.keys())
    if remaining_keys == []:
        print("y")
        yield dictionary
    else:
        key = remaining_keys[0]
        if type(dictionary[key]) is not str and iterable(dictionary[key]):
            print("iter")
            for val in dictionary[key]:
                print("val", val)
                fixed_val_dict=copy.deepcopy(dictionary)
                fixed_val_dict[key]=val
                yield from parameter_grid(fixed_val_dict, remaining_keys[1:])
