from nltk.classify import NaiveBayesClassifier

def train_classifier(training_set, **kwargs):
    classifier = NaiveBayesClassifier.train(training_set)
    return {"sentiment_classifier":classifier}

def classify(sentiment_classifier, tweets, **kwargs):
    classified_tweets = [{tweet:sentiment_classifier.classify(tweet)} for tweet in tweets]
    return {"sentiment_labelled_tweets":classified_tweets}