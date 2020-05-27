import pandas as pd
from preprocessor import Preprocessor
import csv
TEST_LENGTH = 300

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
n_topics = 20
no_top_words = 10

# DATA COLLECTION
train_tweets = pd.read_csv('tweets.csv')
print('Number of tweets : ',len(train_tweets))
tweet_list = []
for i in range(TEST_LENGTH):
    tweet_list.append(train_tweets['tweet'][i])
#print(tweet_list)


# DATA PREPROCESSING
tokens = Preprocessor.preprocess(tweet_list)
tokens = Preprocessor.normalize(tokens)
for i in range(len(tokens)):
    for j in range(len(tokens[i])):
        tokens[i][j] = str(tokens[i][j])

print("Tweet list : ",tweet_list)
print("Tokens : ",tokens)

#wtokens = []
for i in range(len(tokens)):
    #wtokens.append([str(word) for word in tokens[i]])
    tokens[i] = " ".join(tokens[i])
print("sentence tokens : ",tokens)
#print("word tokens : ",wtokens)


#'''
tfidf_vectorizer = TfidfVectorizer(max_df=0.95,
    min_df=2,
    max_features=None,
    stop_words='english')

#Preprocessed version
tfidf = tfidf_vectorizer.fit_transform(tokens)
tfidf_feature_names = tfidf_vectorizer.get_feature_names()

#Raw version
#raw_tfidf = tfidf_vectorizer.fit_transform(tweet_list)
#raw_tfidf_feature_names = tfidf_vectorizer.get_feature_names()

#Word version
#wtokens_tfidf = tfidf_vectorizer.fit_transform(wtokens)
#wtokens_tfidf_feature_names = tfidf_vectorizer.get_feature_names()


print("tfidf_feature_names",tfidf_feature_names)
#print("wtokens tfidf_feature_names",wtokens_tfidf_feature_names)

# Create the LDA model
lda = LatentDirichletAllocation(
    n_components=n_topics,
    max_iter=5,
    learning_method='online',
    learning_offset=50.,
    random_state=0)

# Fit the model on the dataset
lda.fit(tfidf)

def display_topics(model, feature_names, no_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic {} :".format(topic_idx), " ".join([feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]))


display_topics(lda, tfidf_feature_names, no_top_words)




'''
with open('tfidf_feature_names.txt','w') as outfile:
	csv.writer(outfile).writerows(tfidf_feature_names)
with open('raw_tfidf_feature_names.txt','w') as outfile:
	csv.writer(outfile).writerows(raw_tfidf_feature_names)
'''
