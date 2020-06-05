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

def add_params(**kwargs):
    return tuple(kwargs.values())