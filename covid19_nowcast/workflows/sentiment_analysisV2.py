from workflow.pipeline import Pipeline
from workflow.step import Step
from workflow.parameter_grid import parameter_grid as PG
from workflow.metastep import MetaStep
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
                            args=["samples","labels","vectorizing_params"],
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
                    lambda tweets, s_labels, s_proba, n_labels, n_proba: [{**t,
                                                        "sentiment_label":"positive" if s_labels[index]=="4" else "negative",
                                                        "sentiment_proba_trunc":(s_proba[index][0]//0.1)/10,
                                                        "sentiment_proba":s_proba[index][0],
                                                        "neutral_label":n_labels[index],
                                                        "neutral_proba_trunc":(n_proba[index][0]//0.1)/10,
                                                        "neutral_proba":n_proba[index][0],
                                                        "final_sentiment":"neutral" if n_labels[index]=="neutral" or (s_labels[index]=="4" and n_proba[index][0] >= 0.3) else "negative" if s_labels[index]=="0" or s_proba[index][0] > 0.45 else "positive"
                                                        } for index, t in enumerate(tweets)],
                    args=["tweets","sentiment_labels","sentiment_proba","neutral_labels", "neutral_proba"],
                    outputs=["labeled_tweets"],
                    keep_inputs=False,
                    name="labeled_tweets_formatting"
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
                ],name="evaluation"),
            ],name="sentiment_analysis")