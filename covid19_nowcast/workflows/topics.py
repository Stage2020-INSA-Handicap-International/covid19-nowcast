from workflow_manager.pipeline import Pipeline
from workflow_manager.step import Step
from workflow_manager.metastep import MetaStep
from workflow_manager.parameter_grid import parameter_grid as PG
import util
import analysis
from streaming.preparation.preprocessor import Preprocessor

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import numpy as np

def top_topic_tweets_by_proba(tweets, topic_indices, topics, nb_top_tweets=3):
    topics=[{"topic":t, "top_tweets":[]}for t in topics]
    for index, tw in enumerate(tweets):
        topic_index=topic_indices[index]
        if topics[topic_index]["top_tweets"] == [] or not all([tw["topic_proba"]<contestant["topic_proba"] for contestant in topics[topic_index]["top_tweets"]]):
            if(len(topics[topic_index]["top_tweets"])<nb_top_tweets):
                topics[topic_index]["top_tweets"].append(tw)
            else:
                topics[topic_index]["top_tweets"][-1]=tw
                topics[topic_index]["top_tweets"]=sorted(topics[topic_index]["top_tweets"],key=lambda t: t["topic_proba"], reverse=True)
    return topics

pipeline=Pipeline([
        Step(
            util.import_params,
            params=PG({"filepath":["../Datasets/preproc_india0.json"]}),
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
        ),
        Step(
            lambda n_components:(n_components,LatentDirichletAllocation(
                                n_components=n_components,
                                max_iter=5,
                                learning_method='online',
                                learning_offset=50.,
                                random_state=0)),
            params=PG({"n_components":range(5,6,10)}),
            outputs=["n_topics","lda"]
        ),
        Step(
            lambda tfidf, lda: lda.fit(tfidf),
            args=["tfidf", "lda"],
            outputs=["lda"],
        ),
        Step(
            lambda tfidf, lda: lda.transform(tfidf),
            args=["tfidf", "lda"],
            outputs=["topic_probas"],
        ),
        Step(
            lambda topic_probas: [sorted(range(len(a)), key=lambda i: a[i])[-1] for a in topic_probas],
            args=["topic_probas"],
            outputs=["topic_indices"],
        ),
        Step(
            lambda topic_indices, topic_probas: [topic_probas[index][topic_idx] for index, topic_idx in enumerate(topic_indices)],
            args=["topic_indices", "topic_probas"],
            outputs=["topic_proba"]
        ),
        # Step(
        #     lambda topic_indices,topic_probas, min_proba: (min_proba,[topic_indices[index] if probas[topic_indices[index]] >= min_proba else -1 for index, probas in enumerate(topic_proba)]),
        #     args=["topic_indices","topic_probas"],
        #     params=PG({"min_proba":[x/10 for x in range(8,9)]}),
        #     outputs=["min_proba","topic_indices"],
        # ),
        Step(
            util.remove_params,
            args=["tfidf","topic_probas"],
            keep_inputs=False
        ), 
        Step(
            lambda model, feature_names, no_top_words:(no_top_words,[[feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]] for topic in model.components_]),
            args=["lda", "tfidf_feature_names"],
            params=PG({"no_top_words":range(10,11,1)}),
            outputs=["no_top_words","topics"]
        ),
        Step(
            lambda tweets, topic_idx, topic_proba, topics:[{**t, "topic":topics[topic_idx[index]],"topic_proba":topic_proba[index]} for index, t in enumerate(tweets)],
            args=["tweets", "topic_indices", "topic_proba","topics"],
            outputs=["tweets"],
        ),
        # Step(
        #     lambda tweets:(sum([t["topic"]=="N/A" for t in tweets]),sum([t["topic"]=="N/A" for t in tweets])/len(tweets)),
        #     args=["tweets"],
        #     outputs=["N/A count", "% N/A"],
        #     name="count and % N/A"
        # ),
        Step(
            lambda tweets:  [
                            # t if t["topic"] == "N/A" else 
                            {
                                **t,
                                "relevance":sum([
                                        word in t["preproc_text"] for word in t["topic"]
                                    ])/len(t["topic"])
                            } for t in tweets],
            args=["tweets"],
            outputs=["tweets"]
        ),
        Step(
            lambda tweets, min_proba: ({
                    "avg":np.average([t["relevance"]for t in tweets if t["topic_proba"]>=min_proba]), 
                    "std":np.std([t["relevance"]for t in tweets if t["topic_proba"]>=min_proba]), 
                    "min":np.min([t["relevance"]for t in tweets if  t["topic_proba"]>=min_proba]), 
                    "max":np.max([t["relevance"]for t in tweets if t["topic_proba"]>=min_proba]),
                    "percentile":{10*x:np.percentile([t["relevance"]for t in tweets if t["topic_proba"]>=min_proba],10*x) for x in range(1,11)}
                }, min_proba),
            args=["tweets"],
            params=PG({"min_proba":0.8}),
            outputs=["relevance", "min_proba"]
        ),
        Step(
            top_topic_tweets_by_proba,
            args=["tweets", "topic_indices","topics"],
            params=PG({"nb_top_tweets":3}),
            outputs=["topics"]
        ),
        Step(
            analysis.topics.topic_classifier.TopicClassifier.sklearn_print_topics,
            args=["lda", "tfidf_feature_names"],
            params={"no_top_words":10},
            keep_inputs=False
        ),
        # MetaStep(
        #     lambda containers:[print(dc["n_topics"],dc["min_proba"],dc["relevance"]["avg"], dc["N/A count"],dc["% N/A"]) for dc in containers]
        # ),
        Step(
            util.remove_params,
            args=["tweets","topic_indices", "topic_proba"],
            keep_inputs=False
        ),
    ], name="topics analysis")

