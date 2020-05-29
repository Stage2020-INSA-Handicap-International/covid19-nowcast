from covid19_nowcast.streaming.preparation import Preprocessor
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim import models
import gensim


# Provide static methods for 3 different topic classification pipelines.
# pipeline 1 : Gensim library, BOW corpus, LDA model
# pipeline 2 : Gensim library, TF-IDF corpus, LDA model
# pipeline 3 : Sklearn library, TF-IDF corpus, LDA model

class TopicClassifier(object):

    #GENSIM Bag of words model
    @staticmethod
    def gensim_bow(dictionary,tokens):
        bow_corpus = [dictionary.doc2bow(doc) for doc in tokens]
        return bow_corpus

    #GENSIM TF-IDF model
    @staticmethod
    def gensim_tfidf(bow_corpus):
        #TF-IDF
        tfidf = models.TfidfModel(bow_corpus)
        tfidf_corpus = tfidf[bow_corpus]
        return tfidf_corpus

    #GENSIM BOW-based LDA model
    @staticmethod
    def gensim_bow_lda(bow_corpus,dictionary,num_topics=10):
        lda_model = gensim.models.LdaMulticore(bow_corpus, num_topics=num_topics, id2word=dictionary, passes=2, workers=2)
        return lda_model

    #GENSIM TF-IDF-based LDA model
    @staticmethod
    def gensim_tfidf_lda(tfidf_corpus,dictionary,num_topics=10):
        lda_model = gensim.models.LdaMulticore(tfidf_corpus, num_topics=num_topics, id2word=dictionary, passes=2, workers=2)
        return lda_model

    @staticmethod
    def gensim_print_topics(lda_model):
        for idx, topic in lda_model.print_topics(-1):
            print('Topic: {} : {}'.format(idx, topic))
        print("- - - - - - - - -")

    #Scikitlearn TF-IDF model
    @staticmethod
    def sklearn_tfidf(tokens):
        #TODO : try other word embeddings : e.g fastText
        tfidf_vectorizer = TfidfVectorizer(max_df=0.95,
            min_df=2,
            max_features=None,
            stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform(tokens)
        tfidf_feature_names = tfidf_vectorizer.get_feature_names()
        return tfidf_matrix,tfidf_feature_names

    #Scikitlearn TF-IDF-based LDA model
    @staticmethod
    def sklearn_tfidf_lda(tfidf_matrix,num_topics=10):
        #TODO : Author-pooled LDA (needs access to the user's ID)
        #
        # Create the LDA model : maxiter optimal value ? (initially was = 5)
        lda_model = LatentDirichletAllocation(
            n_components=num_topics,
            max_iter=10,
            learning_method='online',
            learning_offset=50.,
            random_state=0)
        # Fit the model on the dataset
        lda_model.fit(tfidf_matrix)
        return lda_model

    @staticmethod
    def sklearn_print_topics(model, feature_names, no_top_words):
        for topic_idx, topic in enumerate(model.components_):
            print("Topic {} :".format(topic_idx), " ".join([feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]))





