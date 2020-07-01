from workflow_manager.pipeline import Pipeline
from workflow_manager.step import Step
from workflow_manager.parameter_grid import parameter_grid as PG
import util
import analysis

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline as SKPipeline
pipeline=Pipeline([
            Pipeline([
                Step(
                    util.add_params,
                    params=PG({"stop_words":["english",None], "min_df":[x for x in range(10,16,1)], "max_df":0.7, "ngram_range":[(1,1), (1,2),(2,2)]}),
                    outputs=["stop_words","min_df", "max_df", "ngram_range"],
                    name="clsf_par"
                ),
                Step(
                    lambda sw,mdf,mxdf,ng:{"stop_words":sw,"min_df":mdf,"max_df":mxdf,"ngram_range":ng},
                    args=["stop_words","min_df", "max_df", "ngram_range"],
                    keep_inputs=False,
                    outputs=["vectorizing_params"]
                ),
                ],
                name="Generating classification params"
            ),
            Step(
                lambda vec_par, classifier:SKPipeline([
                        ('vect', CountVectorizer(**vec_par)),
                        ('tfidf', TfidfTransformer()),
                        ('clf', classifier()),]),
                args=["vectorizing_params"],
                params={"classifier":MultinomialNB},
                outputs=["classifier"],
                name="Creating classifiers"
            ),
            Step(
                util.import_params, 
                params={"filepath":"../Datasets/all_infos.csv", "extension":"csv","unpack":False},
                outputs=["tweets_annotated"],
                read_only_outputs={"tweets_annotated"}
            ),
            Pipeline(
                [
                    Step(
                        lambda x, field:([e[field] for e in x if e["sentiment"] in ["positive", "negative", "neutral", "mixed"]],[e["sentiment"] for e in x if e["sentiment"] in ["positive", "negative", "neutral", "mixed"]]), 
                        args=["tweets_annotated"],
                        outputs=["samples","labels"],
                        params=PG({"field":["full_text"]}),
                        read_only_outputs={"samples"}
                    ),
                    Step(
                        lambda labels:["non_neutral" if l in ["positive", "negative", "mixed"] else l for l in labels], 
                        args=["labels"],
                        outputs=["labels"],
                        keep_inputs=False,
                        read_only_outputs={"labels"}
                    )
                ],
                name="formatting"
            ),
            Step(analysis.sentiment.train_classifier, 
                args=["classifier","samples", "labels"], 
                outputs=["classifier"],
                keep_inputs=True,
                name="train"
            ),
            # Step(
            #     analysis.sentiment.get_coeffs,
            #     args=["classifier"],
            #     outputs=["coeffs"]
            # ),
            Step(
                util.remove_params,
                args=['tweets_annotated'],
                keep_inputs=False
            )
            ],name="neutralizer")