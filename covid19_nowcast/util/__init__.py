def filter_keys(aDict, entries, toKeep=True):
    """
    Removes keys from *aDict* which are not in entries if toKeep is True, or those in entries if toKeep is false
    Input:
        - aDict: a dictionary
        - entries: keys to keep or remove depending on the value of toKeep
        - toKeep: boolean to determine whether to keep or remove keys in *entries*
    Output: 
    """
    toRemove=[]
    for key in aDict.keys():
        if (toKeep and key not in entries) or (not toKeep and key in entries):
            toRemove.append(key)
    for key in toRemove:
        del aDict[key]
    return aDict

def import_params(filepath, unpack=False):
    with open(filepath,"r") as file:
        data=eval(file.read())
        if type(data) is dict and unpack:
            data=tuple(value for value in data.values())
        return data

def add_params(**kwargs):
    return tuple(kwargs.values())

def remove_params(*kwargs):
    pass

import pickle as pk
import datetime
def export_param(param, filepath, pickle=False):
    fullpath=filepath+"_"+str(datetime.datetime.now())
    if pickle:
        with open(fullpath+".pkl", "wb") as file:
            pk.Pickler(file).dump(param)
    else:
        with open(fullpath+".txt", "w") as file:
            file.write(str(param))

def lambda_function():
    pass