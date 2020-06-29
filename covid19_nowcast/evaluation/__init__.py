def score(predicted, target):
    """
    Returns Precision, Recall, F1-Score, and entity counts for labels in *predicted* compared to *target* labels
    """
    assert len(predicted) == len(target)
    scores={"TP":{}, "FP":{}, "FN":{}}
    labels=set()
    for index, pred in enumerate(predicted):
        labels.add(pred)
        labels.add(target[index])
        if pred==target[index]:
            scores["TP"][pred]=scores["TP"].get(pred,0)+1
        else:
            scores["FP"][pred]=scores["FP"].get(pred,0)+1
            scores["FN"][target[index]]=scores["FN"].get(target[index],0)+1
    scores["precision"]={}
    scores["recall"]={}
    scores["f1_score"]={}
    scores["count"]={}
    for label in labels:
        scores["count"][label]=scores["TP"].get(label,0)+scores["FN"].get(label,0)

        denomin=scores["TP"].get(label,0)+scores["FP"].get(label,0)
        if denomin != 0:
            scores["precision"][label]=scores["TP"].get(label,0)/denomin
        else:
            scores["precision"][label]=0

        denomin=scores["TP"].get(label,0)+scores["FN"].get(label,0)
        if denomin != 0:
            scores["recall"][label]=scores["TP"].get(label,0)/denomin
        else:
            scores["recall"][label]=0

        denomin=scores["precision"].get(label,0)+scores["recall"].get(label,0)
        if denomin != 0:
            scores["f1_score"][label]=2*scores["precision"].get(label,0)*scores["recall"].get(label,0)/denomin
        else:
            scores["f1_score"][label]=0
    return scores
