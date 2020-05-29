from covid19_nowcast.streaming.preparation import Preprocessor
from covid19_nowcast.streaming.collection import tweets
from covid19_nowcast.analysis.topics import TopicClassifier

# GLOBAL PARAMETERS
#twitter_query = '#defeatcoronake'
#twitter_query = 'Kenya AND (corona OR coronavirus OR virus OR covid-19 OR covid19)'
twitter_query = '#DefeatCoronaKenya'
misc_keywords = ['amp']
ke_keywords = ['kenyan','kenya','defeatcoronakenya','coronaviruskenya','coronavirusinkenya']
covid_keywords = ['covid','covid-19','covid19','coronavirus','corona','virus']
keywords = misc_keywords + ke_keywords + covid_keywords
n_topics = 10
no_top_words = 10

# DATA COLLECTION : Twitter Crawler version
def collect_data(twitter_query,tweets_nb):
    json_tweets = tweets.crawl_from_raw_query(twitter_query,tweets_nb)
    print("JSON length (nb of tweets) = ",len(json_tweets['tweets']))
    tweet_list = []
    for tweet in json_tweets['tweets']:
        tweet_list.append(tweet['full_text'])
    return tweet_list


# DATA COLLECTION - - - - - - - - - - - - -
tweet_list = collect_data(twitter_query,1000)
# DATA PREPROCESSING - - - - - - - - - - - - -
tokens = Preprocessor.preprocess(tweet_list)
#tokens = Preprocessor.normalize(tokens)
tokens = Preprocessor.delete_words(tokens,keywords)
for i in range(len(tokens)):
    for j in range(len(tokens[i])):
        tokens[i][j] = str(tokens[i][j])
print("Tweet list : ",tweet_list)
print("Tokens : ",tokens)
print("Tokens' length : ",len(tokens))

# DATA ANALYSIS : Topic Classification  - - - -
#Dictionary
dictionary = Preprocessor.filter_extremes(tokens)
#Pipeline 1 : BOW model + Gensim LDA
#Bag of words model
bow_corpus = TopicClassifier.gensim_bow(dictionary,tokens)
#Bag of words based LDA model
bow_lda_model = TopicClassifier.gensim_bow_lda(bow_corpus,dictionary,num_topics=10)
#Bag of words based LDA Topic classification
print("Gensim BOW LDA Model Topics - - - - - - - - - - - - - - - - - - - -")
TopicClassifier.gensim_print_topics(bow_lda_model)

#Pipeline 2 : TF-IDF model + Gensim LDA
#TF-IDF model
tfidf_corpus = TopicClassifier.gensim_tfidf(bow_corpus)
#TF-IDF based LDA model
tfidf_lda_model = TopicClassifier.gensim_tfidf_lda(tfidf_corpus,dictionary,num_topics=10)
#TF-IDF based LDA Topic classification
print("Gensim TF-IDF LDA Model Topics - - - - - - - - - - - - - - - - - - - -")
TopicClassifier.gensim_print_topics(tfidf_lda_model)

#Pipeline 3 : TF-IDF model + Scikitlearn LDA
#Convert tokens to sentences
for i in range(len(tokens)):
    tokens[i] = " ".join(tokens[i])
#TF-IDF model
sklearn_tfidf_matrix, sklearn_tfidf_feature_names = TopicClassifier.sklearn_tfidf(tokens)
#TF-IDF based LDA Topic classification
sklearn_tfidf_lda_model = TopicClassifier.sklearn_tfidf_lda(sklearn_tfidf_matrix,num_topics=10)
print("SkLearn TF-IDF LDA Model Topics - - - - - - - - - - - - - - - - - - - -")
TopicClassifier.sklearn_print_topics(sklearn_tfidf_lda_model, sklearn_tfidf_feature_names, no_top_words)
