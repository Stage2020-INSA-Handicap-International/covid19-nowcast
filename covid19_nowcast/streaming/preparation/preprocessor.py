import pandas as pd
import spacy
from collections import Counter
from nltk import FreqDist
from collections import defaultdict
import matplotlib.pyplot as plt
import progressbar

#Domain-dependent preprocessing : Lemmatization, Stopwords removal, Text-enrichment (POS-tagging)
#Should-dos : Normalization (standardize identical words e.g b4 and before), Lowercasing, Noise-removal (e.g punctuation, non-alpha chars. The noise definition is domain-dependent)
#Each layer added needs to be quantitatively and qualitatively verified as a meaningful layer

class Preprocessor(object):

    @staticmethod
    def flatten_2d_array(array):
        flattened_array = []
        for i in range(len(array)):
            for j in range(len(array[i])):
                flattened_array.append(str(array[i][j]))
        return flattened_array

    ######### Data Collection #########
    #TODO: when access to Twitter's API is granted


    ######### Data Preprocessing #########
    #Faire un jupyter notebook avec des visualisations des résultats selon le preprocessing qu'on fait de manière à voir les plus pertinents
    # la visualisation peut se faire à travers des word frequencies par ex

    #Tokenization, Lowercasing, Lemmatization, Stopword Removal
    @staticmethod
    def preprocess(tweets_list, **kwargs):
        nlp = spacy.load("en_core_web_sm")
        tokens = []
        for i in progressbar.progressbar(range(len(tweets_list))):
            doc = nlp(str(tweets_list[i]))
            #for token in doc:
                #print(token,token.pos_,token.lemma_,token.is_stop)
            #Remove stop words and non-alpha words
            tweet_tokens = [token.lemma_ for token in doc if (not token.is_stop and token.is_alpha)]
            tokens.append(tweet_tokens)
        return tokens

    #Normalization (e.g 'b4' -> 'before')
    #Two common approaches :
    # - Dictionary mappings (easiest) approaches
    # - Statistical machine translation (SMT) and correction-based approaches
    @staticmethod
    def normalize(tokens):
        abbreviation_list = pd.read_csv('top_50_acronyms.csv')
        #print('Number of abbreviations : ',len(abbreviation_list))
        #print(abbreviation_list)
        abbreviation_dict = dict()
        for i in range(len(abbreviation_list)):
            abbreviation_dict[abbreviation_list['abbreviation'][i]] = abbreviation_list['word'][i]
        #print(abbreviation_dict)

        for i in range(len(tokens)):
            for j in range(len(tokens[i])):
                if tokens[i][j] in abbreviation_dict:
                    #delete the abbreviation
                    tokens[i].pop(j)
                    #append the word(s)
                    abbreviation_meaning = abbreviation_dict[tokens[i][j]].split(" ")
                    for word in abbreviation_meaning:
                        tokens[i].append(word)
        return tokens

    #POS-Tagging
    @staticmethod
    def pos_tag(corpus):
        return []
        #pos_tags = nltk.pos_tag(tokenized_first_tweet)
        #print(pos_tags)


    #Frequency Analysis
    @staticmethod
    def n_most_common_words(n,raw_tweets):
        word_freq = Counter(raw_tweets)
        # 5 commonly occurring words with their frequencies
        common_words = word_freq.most_common(n)
        return common_words

    @staticmethod
    def explore_dataset(tokens):
        corpora = defaultdict(list)

        # Création d'un corpus de tokens par artiste
        for i in range(len(tokens)):
            corpora[i] = tokens[i]

        stats, freq = [], dict()

        for k, v in corpora.items():
            freq[k] = FreqDist(v)
            stats.append(len(v))

        return (freq, stats, corpora)

    @staticmethod
    def plot_top_n_tweets_length(n,tokens):
        # Récupération des comptages
        freq, stats, corpora = Preprocessor.explore_dataset(tokens)

        #Affichage
        fig,axes = plt.subplots(ncols=2)
        df = pd.DataFrame(stats, columns=['Total words'])
        df = df.sort_values(by='Total words',ascending=False)
        df_longest_tweets = df.nlargest(n,'Total words')
        df_longest_tweets.plot(ax=axes[0],kind='bar', color="#f56900", title='Top 20 des tweets par longueur décroissante sur un index de '+ str(len(tokens)) +' tweets')

        df.boxplot(ax=axes[1],column='Total words')

        plt.show(block=True)


'''
#Display
for i in range(200):
    print(tweet_list[i])
    print(tokens[i])
    print("---")
'''



'''
with open('tokens.txt','w') as outfile:
	csv.writer(outfile, delimiter=' ').writerows(tokens)
'''

















