# Classification en topics du corpus twitter sur l'intégralité de l'intervalle temporel allant de Janvier à Juin 2020
# sans division temporelle.

from covid19_nowcast.streaming.preparation import Preprocessor
from covid19_nowcast.streaming.collection import tweets
from covid19_nowcast.streaming.collection import covid19_api
from covid19_nowcast.analysis.topics import TopicClassifier
import json
from datetime import datetime

# GLOBAL PARAMETERS
#twitter_query = '#defeatcoronake'
twitter_query = 'Kenya AND (corona OR coronavirus OR virus OR covid-19 OR covid19)'
#twitter_query = '#DefeatCoronaKenya'
misc_keywords = ['amp']
ke_keywords = ['kenyan','kenya','defeatcoronakenya','coronaviruske','coronaviruskenya','coronavirusinkenya']
covid_keywords = ['covid','covid-19','covid19','coronavirus','corona','virus','pandemic']
keywords = misc_keywords + ke_keywords + covid_keywords
n_topics = 10
no_top_words = 10


def get_china_covid_numbers():
        covid_numbers_china = covid19_api.get_countries_info(["China"])
        with open('china_covid_numbers.json','w') as outfile:
                json.dump(covid_numbers_china,outfile)

def format_china_covid_numbers():
        with open('china_covid_numbers.json') as outfile:
                china_covid_numbers = json.load(outfile)
        formatted_china_covid_numbers = []
        china_json = china_covid_numbers['countries_covid19']['China']
        for i in range(len(china_json)):
                date_exists = False
                date = china_json[i]['Date']
                #Si la date existe déjà dans le json à dates uniques
                for j in range(len(formatted_china_covid_numbers)):
                        if date == formatted_china_covid_numbers[j]["Date"]:
                                date_exists = True
                                formatted_china_covid_numbers[j]["Confirmed"] += china_json[i]["Confirmed"]
                                formatted_china_covid_numbers[j]["Deaths"] += china_json[i]["Deaths"]
                                formatted_china_covid_numbers[j]["Recovered"] += china_json[i]["Recovered"]
                                formatted_china_covid_numbers[j]["Active"] += china_json[i]["Active"]
                #Si elle n'existe pas, la créer
                if not date_exists:
                        new_entry = {"Confirmed": 0, "Deaths": 0, "Recovered": 0, "Active": 0, "Date": str(china_json[i]["Date"])}
                        formatted_china_covid_numbers.append(json.loads(json.dumps(new_entry)))
        with open('china_covid_numbers.json','w') as outfile:
                json.dump(formatted_china_covid_numbers,outfile)

# Date formatting
def format_date(json_tweets):
    for i in range(len(json_tweets['tweets'])):
        raw_date = json_tweets['tweets'][i]['created_at']
        date = datetime.strptime(raw_date,'%a %b %d %H:%M:%S %z %Y')
        month = str(date.month) if int(date.month)>10 else '0'+str(date.month)
        day = str(date.day) if int(date.day)>10 else '0'+str(date.day)
        #json_tweets['tweets'][i]['formatted_date'] = str(date.year) + '-' + month + '-' + day
        #print("year : ",str(date.year)," - month : ",month," - day : ",day," - Full date : ",str(date.year) + month + day)
        json_tweets['tweets'][i]['formatted_date'] = str(date.year) + month + day
    with open('2020_formatted_tweets.json','w') as outfile:
            json.dump(json_tweets,outfile)

#'''
# DATA COLLECTION : Twitter Crawler version
def collect_data(twitter_query,tweets_nb):
    #First run : crawl tweets
    #json_tweets = tweets.crawl_from_raw_query(twitter_query,tweets_nb)
    #print("JSON length (nb of tweets) = ",len(json_tweets['tweets']))
    #with open('2020_tweets.json','w') as outfile:
	    #json.dump(json_tweets,outfile)

    #Further runs : open the json crawled tweets
    with open('2020_tweets.json') as json_file:
	    json_tweets = json.load(json_file)
    tweet_list = []
    for tweet in json_tweets['tweets']:
        tweet_list.append(tweet['full_text'])
    return tweet_list


def get_countries_info():
    covid_numbers_ke = covid19_api.get_countries_info(["Kenya"])
    with open('kenya_covid_numbers.json','w') as outfile:
            json.dump(covid_numbers_ke,outfile)


tweet_list = collect_data(twitter_query,30000)
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
#for i in range(len(tokens)):
    #tokens[i] = " ".join(tokens[i])
#TF-IDF model
sklearn_tfidf_matrix, sklearn_tfidf_feature_names = TopicClassifier.sklearn_tfidf(tokens)
#TF-IDF based LDA Topic classification
sklearn_tfidf_lda_model = TopicClassifier.sklearn_tfidf_lda(sklearn_tfidf_matrix,num_topics=20)
print("SkLearn TF-IDF LDA Model Topics - - - - - - - - - - - - - - - - - - - -")
TopicClassifier.sklearn_print_topics(sklearn_tfidf_lda_model, sklearn_tfidf_feature_names, no_top_words)


'''
with open('tweets.json') as json_file:
	json_tweets = json.load(json_file)
tweets = []
for tweet in json_tweets['tweets']:
    date = tweet['created_at']
    formated_date = ' '.join(date.split()[1:3])+' '+date.split()[5]
    tweets.append([formated_date,tweet['full_text']])

#La démarche est la suivante : Pour tester la pertinence de la classification en topics, je prends un topic (donc une array de tokens) et je print pour
#chaque token les tweets où il apparaît. Si dans les tweets où il apparaît les autres tokens de la même array apparaîssent alors le topic est pertinent.
#Par exemple si Topic 0 = ['loan','food','imf','bank'] en cherchant les tweets où 'loan' apparaît je dois trouver des apparitions de termes reliés à 'food',
#'imf', et 'bank'
topics = ['youth', 'beat', 'entrepreneur', 'curve', 'sell', 'soap', 'help', 'refugee', 'kill', 'type']
for topic_word in topics:
    for tweet in tweets:
        if topic_word in tweet[1]:
            print(topic_word,' - - - - ',tweet[0],'- -',tweet[1])
    print('- - - - - - - ')
'''



'''

#'''
