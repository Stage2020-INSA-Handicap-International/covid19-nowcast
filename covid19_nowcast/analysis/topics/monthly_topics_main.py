# Classification en topics du corpus twitter sur l'intégralité de l'intervalle temporel allant de Janvier à Juin 2020
# avec division temporelle (i.e une série de topics pour chaque mois)


import json
from covid19_nowcast.streaming.collection import covid19_api
from covid19_nowcast.streaming.preparation import Preprocessor
from covid19_nowcast.analysis.topics import TopicClassifier
from covid19_nowcast.streaming.collection import tweets
n_topics = 4
no_top_words = 6
misc_keywords = ['amp']
africa_keywords = ['africa','african','africans','Africa','African','Africans','AFRICA','AFRICAN','AFRICANS']
ke_keywords = ['kenyan','kenya','defeatcoronakenya','coronaviruske','coronaviruskenya','coronavirusinkenya']
covid_keywords = ['covid','covid-19','covid19','coronavirus','corona','virus','pandemic']
weekdays_keywords = ['mon','tue','wed','thu','fri','sat','sun']
keywords = misc_keywords + africa_keywords + ke_keywords + covid_keywords + weekdays_keywords

def collect_monthly_data(month,json_tweets_filename):
    with open(json_tweets_filename) as json_file:
	    json_tweets = json.load(json_file)
    tweet_list = []
    for tweet in json_tweets['tweets']:
        if tweet['created_at'][4:7] == month:
            tweet_list.append([tweet['created_at'][0:10],tweet['user']['name'],tweet['full_text']])
    return tweet_list

def aggregate_monthly_data(months,json_tweets_filename):
    monthly_tweets = []
    nb_tweets = 0
    for month in months:
        month_tweet_list = collect_monthly_data(month,json_tweets_filename)
        monthly_tweets.append(month_tweet_list)
        nb_tweets += len(month_tweet_list)
    print("Nb of tweets within the months parameter : ",nb_tweets)
    return monthly_tweets


def get_countries_info():
    covid_numbers_ke = covid19_api.get_countries_info(["Kenya"])
    with open('kenya_covid_numbers.json','w') as outfile:
            json.dump(covid_numbers_ke,outfile)


# TOPIC CLASSIFICATION PER MONTH - - - - - - - - - - - - -
def classify_topics_per_month(monthly_tweets):
    counter = 0
    months = ['Jan','Feb','Mar','Apr','May','Jun']
    for single_month_tweet_list in monthly_tweets:
        #PREPROCESSING
        tokens = Preprocessor.preprocess(single_month_tweet_list)
        #tokens = Preprocessor.normalize(tokens)
        tokens = Preprocessor.delete_words(tokens,keywords)
        for i in range(len(tokens)):
            for j in range(len(tokens[i])):
                tokens[i][j] = str(tokens[i][j])
        print('\n')
        print(months[counter].upper(),"- - - - - - - - - - - - - - ")
        counter += 1
        #print("Tweet list : ",single_month_tweet_list)
        #print("Tokens : ",tokens)
        print("Nb of tweets : ",len(tokens))


        #TOPIC CLASSIFICATION : Pipeline 3 : TF-IDF model + Scikitlearn LDA
        #TF-IDF model
        sklearn_tfidf_matrix, sklearn_tfidf_feature_names = TopicClassifier.sklearn_tfidf(tokens)
        #TF-IDF based LDA Topic classification
        sklearn_tfidf_lda_model = TopicClassifier.sklearn_tfidf_lda(sklearn_tfidf_matrix,num_topics=n_topics)
        print("SkLearn TF-IDF LDA Model Topics - - - - - - - - - - - - - - - - - - - -")
        TopicClassifier.sklearn_print_topics(sklearn_tfidf_lda_model, sklearn_tfidf_feature_names, no_top_words)


        #TOPIC CLASSIFICATION : Pipeline 2 : Gensim TF-IDF model + Gensim LDA
        #TF-IDF model
        dictionary = Preprocessor.filter_extremes(tokens)
        bow_corpus = TopicClassifier.gensim_bow(dictionary,tokens)
        tfidf_corpus = TopicClassifier.gensim_tfidf(bow_corpus)
        #TF-IDF based LDA Topic classification
        tfidf_lda_model = TopicClassifier.gensim_tfidf_lda(tfidf_corpus,dictionary,num_topics=n_topics)
        print("Gensim TF-IDF LDA Model Topics - - - - - - - - - - - - - - - - - - - -")
        TopicClassifier.gensim_print_topics(tfidf_lda_model)

# TWEETS COLLECTION : INDIA
'''
twitter_query = '(India OR INDIA or india) AND (corona OR coronavirus OR virus OR covid-19 OR covid19)'
json_tweets = tweets.crawl_from_raw_query(twitter_query,50000)
print("JSON length (nb of tweets) = ",len(json_tweets['tweets']))
with open('2020_tweets_india.json','w') as outfile:
    json.dump(json_tweets,outfile)
'''
months = ['Jan','Feb','Mar','Apr','May','Jun']
monthly_tweets = aggregate_monthly_data(months,'2020_tweets_india.json')
classify_topics_per_month(monthly_tweets)





# TOPIC VERIFICATION  - - - - - - - - - - - - -
'''
#months = ['Jan','Feb','Mar','Apr','May','Jun']
months = ['Jan','Feb','Mar','Apr','May','Jun']
monthly_tweets = aggregate_monthly_data(months)

#La démarche est la suivante : Pour tester la pertinence de la classification en topics, je prends un topic (donc une array de tokens) et je print pour
#chaque token les tweets où il apparaît. Si dans les tweets où il apparaît les autres tokens de la même array apparaîssent alors le topic est pertinent.
#Par exemple si Topic 0 = ['loan','food','imf','bank'] en cherchant les tweets où 'loan' apparaît je dois trouver des apparitions de termes reliés à 'food',
#'imf', et 'bank'.
#topics = array contenant un topic précédemment classifié qu'on va venir vérifier manuellement (i.e en regardant où apparaissent les termes
#qu'il regroupe dans les tweets)
topics = ['crisis', 'response', 'fund', 'work', 'discuss', 'country', 'billion', 'economy', 'journalist', 'fact']
for topic_word in topics:
    #April
    for tweet in monthly_tweets[4]:
        if topic_word in tweet[2]:
            print(topic_word,' - - - - ',tweet[0],'- -',tweet[1],'- -',tweet[2])
    print('- - - - - - - ')
'''
