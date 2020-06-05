from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import numpy as np
import spacy

def train_classifier(texts_list, labels, **kwargs):
    text_clf = Pipeline([('vect', CountVectorizer()),
                         ('tfidf', TfidfTransformer()),
                         ('clf', MultinomialNB()),])
    text_clf = text_clf.fit(texts_list, labels)
    return text_clf

def classify(sentiment_classifier, texts_list, **kwargs):
    predicted = sentiment_classifier.predict(texts_list)
    return list(map(str,list(predicted)))

def tweets_to_text(tweets, **kwargs):
    tweets_text=[tweet["full_text"] for tweet in tweets]
    return tweets_text
