from workflow_manager.pipeline import Pipeline
from workflow_manager.step import Step
from workflow_manager.parameter_grid import parameter_grid as PG
import util
import analysis
from streaming.preparation.preprocessor import Preprocessor

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

pipeline=Pipeline([
        Step(
            util.import_params,
            params={"filepath":"../Datasets/preproc_india.json"},
            outputs=["tweets"]
        ),
        Step(
            lambda tweets, clsf:(clsf.fit_transform([t["preproc_text"] for t in tweets]),clsf.get_feature_names()),
            args=["tweets"],
            params={"clsf":TfidfVectorizer(max_df=0.95,
                                            min_df=2,
                                            max_features=None,
                                            stop_words='english')
                    },
            outputs=["tfidf","tfidf_feature_names"],
            keep_inputs=False
        ),
        Step(
            util.add_params,
            params={"lda":LatentDirichletAllocation(
                                n_components=20,
                                max_iter=5,
                                learning_method='online',
                                learning_offset=50.,
                                random_state=0)
                                },
            outputs=["lda"]
        ),
        Step(
            lambda tfidf, lda: lda.fit(tfidf),
            args=["tfidf", "lda"],
            outputs=["lda"],
            keep_inputs=False
        ),
        Step(
            lambda model, feature_names, no_top_words:[[feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]] for topic in model.components_],
            args=["lda", "tfidf_feature_names"],
            params={"no_top_words":10},
            outputs=["topics"]
        ),
        Step(
            analysis.topics.topic_classifier.display_topics,
            args=["lda", "tfidf_feature_names"],
            params={"no_top_words":10},
            keep_inputs=False
        ),
    ], name="topics analysis")