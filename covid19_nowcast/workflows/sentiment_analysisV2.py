from workflow_manager.pipeline import Pipeline
from workflow_manager.step import Step
from workflow_manager.parameter_grid import parameter_grid as PG
from workflow_manager.metastep import MetaStep
from workflow import meta
import util
import analysis
import evaluation
import numpy as np
from workflows.test import pipeline as sentiment_clsf_pipe
from workflows.neutralizer import pipeline as neutral_clsf_pipe
pipeline=Pipeline([
                Pipeline(
                    [
                        Step(
                            lambda rn:rn,
                            args=["vectorizing_params"],
                            outputs=["sent_params"],
                            keep_inputs=False
                        ),
                        sentiment_clsf_pipe,
                        Step(
                            lambda labels, test_tw: (labels, test_tw),
                            args=["labels","test_tweets"],
                            outputs=["sentiment_labels","preproc_tweets"],
                            keep_inputs=False
                        ),
                        Step(
                            util.remove_params,
                            args=["preproc_tweets"],
                            keep_inputs=False
                        ),
                    ],
                    name="Getting sentiment labels"
                ),
                Pipeline(
                    [
                        neutral_clsf_pipe,
                        Step(
                            util.remove_params,
                            args=["samples","labels"],
                            keep_inputs=False
                        ),
                        Step(
                            lambda rn:rn,
                            args=["vectorizing_params"],
                            outputs=["neutral_params"],
                            keep_inputs=False
                        ),
                        Step(
                            lambda clsf: clsf,
                            args=["classifier"],
                            outputs=["neutral_clsf"],
                            keep_inputs=False,
                            name="rename_clsf"
                        ),
                        Pipeline(
                            [
                                Step(
                                    util.import_params, 
                                    params={"filepath":"../Datasets/2020_tweets.json", "unpack":False},
                                    outputs=["tweets"],
                                    read_only_outputs={"tweets"}
                                ),
                                Step(
                                    lambda tweets:[t["full_text"] for t in tweets],
                                    args=["tweets"],
                                    outputs=["full_texts"],
                                    keep_inputs=False,
                                    name="full_texts_getter"
                                ),
                            ],
                            name="Getting full texts from tweets"
                        ),
                        Step(
                            analysis.sentiment.classify, 
                            args=["neutral_clsf","full_texts"],
                            outputs=["neutral_labels"],
                            keep_inputs=True
                        ),
                        Step(
                            analysis.sentiment.classify, 
                            args=["neutral_clsf","full_texts"],
                            outputs=["neutral_proba"],
                            params={"return_type":"proba"},
                            keep_inputs=False
                        ),
                    ],
                    name="Getting_neutrality_labels"
                ),
                Step(
                    util.import_params, 
                    params={"filepath":"../Datasets/Kenya_tweets_sentiments.json", "unpack":False},
                    outputs=["tweets"],
                    read_only_outputs={"tweets"},
                    name="Getting manual sentiment annotations"
                ),
                Step(
                    util.add_params,
                    params=PG({"threshold_pos":[x/100 for x in range(10,50,1)],"threshold_neg":[x/100 for x in range(46,47)]}),
                    outputs=["threshold_pos","threshold_neg"],
                    name="thresholds"
                ),
                Step(
                    lambda tweets, s_labels, s_proba, n_labels, n_proba, th_pos, th_neg: [{**t,
                                                        "sentiment_label":"positive" if s_labels[index]=="4" else "negative",
                                                        "sentiment_proba_trunc":(s_proba[index][0]//0.1)/10,
                                                        "sentiment_proba":s_proba[index][0],
                                                        "neutral_label":n_labels[index],
                                                        "neutral_proba_trunc":(n_proba[index][0]//0.1)/10,
                                                        "neutral_proba":n_proba[index][0],
                                                        "final_sentiment":"neutral" if n_labels[index]=="neutral" or (s_labels[index]=="4" and n_proba[index][0] >= th_pos) else "negative" if s_labels[index]=="0" or s_proba[index][0] > th_neg else "positive"
                                                        } for index, t in enumerate(tweets)],
                    args=["tweets","sentiment_labels","sentiment_proba","neutral_labels", "neutral_proba","threshold_pos","threshold_neg"],
                    outputs=["labeled_tweets"],
                    #keep_inputs=False,
                    name="labeled_tweets_formatting"
                ),
                Step(
                    util.remove_params,
                    args=["tweets","sentiment_labels","sentiment_proba","neutral_labels", "neutral_proba"],
                    keep_inputs=False
                ),
                Pipeline([
                    Step(
                        lambda tw: ([t["final_sentiment"] for t in tw if t["sentiment"]!="N/A"],[t["sentiment"] for t in tw if t["sentiment"]!="N/A"]),
                        args=["labeled_tweets"],
                        outputs=["pred_labels","true_labels"]
                    ),
                    Step(
                        evaluation.score,
                        args=["pred_labels","true_labels"],
                        outputs=["scores"],
                        keep_inputs=False,
                    ),
                    Step(
                        lambda scores:np.sum([val*scores["count"][key] for key,val in scores["f1_score"].items()])/np.sum([val for val in scores["count"].values()]),
                        args=["scores"],
                        outputs=["summary"],
                        name="summary"
                    ),
                    MetaStep(  
                        meta.top_N,
                        params={"n_best":5, "criterion":lambda data:data["summary"]}
                    ),
                    Step(
                        lambda summary, vec_sent, vec_neut, field, th_pos, th_neg: print(
                                                                                    summary, 
                                                                                    "sent", vec_sent,
                                                                                    "neutr",vec_neut,"field:", field,
                                                                                    "thresholds pos/neg", th_pos,th_neg
                                                                                    ),
                        args=["summary", "sent_params", "neutral_params", "field","threshold_pos","threshold_neg"]
                    ),
                ],name="evaluation"),
            ],name="sentiment_analysis")