from workflow.pipeline import Pipeline
from workflow.step import Step
from workflow.parameter_grid import parameter_grid as PG
import util
import analysis

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
                            keep_inputs=False
                        ),
                    ],
                    name="Getting_neutrality_labels"
                ),
                Step(
                    util.import_params, 
                    params={"filepath":"../Datasets/all_infos.csv", "extension":"csv", "unpack":False},
                    outputs=["tweets"],
                    read_only_outputs={"tweets"},
                    name="Getting manual sentiment annotations"
                ),
                Step(
                    lambda tweets, s_labels, n_labels: [{**t,
                                                        "sentiment_label":s_labels[index],
                                                        "neutral_label":n_labels[index]
                                                        } for index, t in enumerate(tweets)],
                    args=["tweets","sentiment_labels","neutral_labels"],
                    outputs=["labeled_tweets"],
                    keep_inputs=False,
                    name="labeled_tweets_formatting"
                ),
            ],name="sentiment_analysis")