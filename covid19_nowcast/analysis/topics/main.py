#import sys
#sys.path.append('/Users/mac/Desktop/covid19-nowcast-africa/covid19_nowcast/streaming/preparation')
import pandas as pd
from preprocessor import Preprocessor
TEST_LENGTH = 100

#print(sys.path)

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

print(tokens)

