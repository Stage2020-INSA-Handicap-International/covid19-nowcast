from nltk.classify import NaiveBayesClassifier

def train_classifier(bag_of_words, **kwargs):
    classifier = NaiveBayesClassifier.train(bag_of_words)
    return {"sentiment_classifier":classifier}