import pandas as pd
from preprocessor import Preprocessor
DATASET_LENGTH = 31962
TEST_LENGTH = 100

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

# FREQUENCY ANALYSIS
print("5 most common words before preprocessing :")
raw_tweets = Preprocessor.flatten_2d_array(tweet_list)
common_words = Preprocessor.n_most_common_words(10,raw_tweets)
print(common_words)
print('-----')
print("5 most common words after preprocessing :")
raw_preprocessed_tweets = Preprocessor.flatten_2d_array(tokens)
common_preprocessed_words = Preprocessor.n_most_common_words(10,raw_preprocessed_tweets)
print(common_preprocessed_words)

# DATA VIZ
Preprocessor.plot_top_n_tweets_length(100,tokens)
