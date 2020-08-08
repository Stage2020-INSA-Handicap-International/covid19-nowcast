import covid19_nowcast.analysis.topics.topic_classifier
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

def topicalize_tweets(tweets, nb_topics):
    topic_indices, topic_proba, topics=topicalize_texts([t["preproc_text"] for t in tweets],nb_topics)
    tweets=[{**t, "topic_id":topic_indices[index],
                        #"topic":topics[topic_idx[index]],
                        "topic_proba":topic_proba[index]} for index, t in enumerate(tweets)]
    return tweets, topics

def topicalize_texts(preproc_texts, nb_topics, no_top_words=10):
    max_df=0.95 if len(preproc_texts)>2 else 1.0
    min_df=2 if max_df*len(preproc_texts)>2 else 0
    tfidf=TfidfVectorizer(max_df=max_df,min_df=min_df,max_features=None,stop_words='english')
    tfidf_res=tfidf.fit_transform(preproc_texts)
    tfidf_feature_names=tfidf.get_feature_names()

    lda=LatentDirichletAllocation(n_components=nb_topics,
                                max_iter=5,
                                learning_method='online',
                                learning_offset=50.,
                                random_state=0)
    topic_probas=lda.fit_transform(tfidf_res)

    topic_indices=[sorted(range(len(a)), key=lambda i: a[i])[-1] for a in topic_probas]
    topic_proba=[topic_probas[index][topic_idx] for index, topic_idx in enumerate(topic_indices)]

    topics=[[tfidf_feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]] for topic in lda.components_]
    return topic_indices, topic_proba, topics

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