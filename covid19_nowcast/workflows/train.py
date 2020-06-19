from workflow.pipeline import Pipeline
from workflow.step import Step
from workflow.parameter_grid import parameter_grid as PG
import util
import analysis

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import ComplementNB
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline as SKPipeline
pipeline=Pipeline([
            Step(
                util.add_params,
                params=PG({"stop_words":"english", "min_df":[x/100000 for x in range(1,10)], "max_df":0.7, "ngram_range":[(1,1), (1,2)]}),
                outputs=["stop_words","min_df", "max_df", "ngram_range"],
                name="clsf_par"
            ),
            Step(
                lambda sw,mdf,mxdf,ng:{"stop_words":sw,"min_df":mdf,"max_df":mxdf,"ngram_range":ng},
                args=["stop_words","min_df", "max_df", "ngram_range"],
                keep_inputs=False,
                outputs=["vectorizing_params"]
            ),
            Step(
                lambda vec_par, classifier:SKPipeline([
                        ('vect', CountVectorizer(**vec_par)),
                        ('tfidf', TfidfTransformer()),
                        ('clf', classifier()),]),
                args=["vectorizing_params"],
                params=PG({"classifier":[MultinomialNB,SGDClassifier]}),
                outputs=["classifier"],
                name="classifier",
                export_path="output/<classifier.params[classifier]>_<clsf_par.params[stop_words,min_df,max_df,ngram_range]>"
            ),
            Step(
                util.import_params, 
                params={"filepath":"../Datasets/preprocLabeledDict1p6M.json", "unpack":True},
                outputs=["tweets","labels"],
                read_only_outputs={"tweets","labels"}
            ),
            Step(analysis.sentiment.train_classifier, 
                args=["classifier","tweets", "labels"], 
                outputs=["classifier"],
                keep_inputs=False,
                name="train"
            ),
            Step(
                analysis.sentiment.get_coeffs,
                args=["classifier"],
                outputs=["coeffs"],
                export_path="output/coeff_<classifier.params[classifier]>_<clsf_par.params[stop_words,min_df,max_df,ngram_range]>"
            ),
            Step(
                util.remove_params,
                args=["coeffs"],
                keep_inputs=False
            )
            ],name="sentiment_analysis")