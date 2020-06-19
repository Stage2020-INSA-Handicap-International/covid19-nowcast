from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import ComplementNB
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
import numpy as np
import spacy

def train_classifier(pipeline, texts_list, labels):
    pipeline = pipeline.fit(texts_list, labels)
    return pipeline

def train_MNB_classifier(texts_list, labels):
    text_clf = Pipeline([('vect', CountVectorizer(stop_words="english", min_df=0.000005, max_df=0.7, ngram_range=(1,1))),
                         ('tfidf', TfidfTransformer()),
                         ('clf', MultinomialNB()),])
    text_clf = text_clf.fit(texts_list, labels)
    return text_clf

def train_CNB_classifier(texts_list, labels):
    text_clf = Pipeline([('vect', CountVectorizer(stop_words="english")),
                         ('tfidf', TfidfTransformer()),
                         ('clf', ComplementNB()),])
    text_clf = text_clf.fit(texts_list, labels)
    return text_clf

def train_SVM_classifier(texts_list, labels):
    text_clf = Pipeline([('vect', CountVectorizer(stop_words="english", min_df=0.000005, max_df=0.7, ngram_range=(1,1))),
                         ('tfidf', TfidfTransformer()),
                         ('clf', SGDClassifier(loss='log', penalty='l2',alpha=1e-3, verbose=True, n_jobs=-1)),
                        ])
    text_clf = text_clf.fit(texts_list, labels)
    return text_clf

def train_RF_classifier(texts_list, labels):
    text_clf = Pipeline([('vect', CountVectorizer(stop_words="english")),
                         ('tfidf', TfidfTransformer()),
                         ('clf-rf', RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=0, verbose=10)),])
    text_clf = text_clf.fit(texts_list, labels)
    return text_clf

def classify(sentiment_classifier, texts_list, return_type="class"):
    predicted = []
    if return_type=="class":
        predicted = list(map(str,list(sentiment_classifier.predict(texts_list))))
    elif return_type=="proba":
        try:
            predicted = list(map(list,list(sentiment_classifier.predict_proba(texts_list))))
        except:
            predicted = list(map(list,list(sentiment_classifier.decision_function(texts_list))))
    return predicted

def tweets_to_text(tweets):
    tweets_text=[tweet["full_text"] for tweet in tweets]
    return tweets_text

def get_coeffs(sentiment_classifier):
    coeffs=[]
    coeff_location=None
    if hasattr(sentiment_classifier["clf"], "feature_log_prob_"):
        print("feature")
        coeff_location=sentiment_classifier["clf"].feature_log_prob_
    else:
        coeff_location=sentiment_classifier["clf"].coef_
    for class_idx, class_ID in enumerate(coeff_location):
        class_name=str(sentiment_classifier["clf"].classes_[class_idx])
        for index, name in enumerate(sentiment_classifier["vect"].get_feature_names()):
            infos={"class":class_name, "word":name, "log_proba":float(class_ID[index])}
            if hasattr(sentiment_classifier["clf"], "feature_count_"):
                infos["count"]=[float(classes[index][class_idx]) for classes in sentiment_classifier["clf"].feature_count_]
            coeffs.append(infos)
    return coeffs
    
def spellcheck(texts_list):
    import pkg_resources
    from symspellpy import SymSpell, Verbosity

    sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
    dictionary_path = pkg_resources.resource_filename(
        "symspellpy", "frequency_dictionary_en_82_765.txt")
    bigram_path = pkg_resources.resource_filename(
        "symspellpy", "frequency_bigramdictionary_en_243_342.txt")
    # term_index is the column of the term and count_index is the
    # column of the term frequency
    sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
    sym_spell.load_bigram_dictionary(bigram_path, term_index=0, count_index=2)

    # max edit distance per lookup (per single word, not per whole input string)
    texts_list = [sym_spell.lookup_compound(text, max_edit_distance=2) for text in texts_list]

    return texts_list
