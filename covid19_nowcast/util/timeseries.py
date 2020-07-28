import pandas as pd
import matplotlib.pyplot as plt
import json
import datetime


with open("2020_tweets.json") as json_file:
  json_tweets = json.load(json_file)

# Create a data structure that contains for each unique day the nb
# of tweets in that day
# (peut devenir chiant si on prévoit de changer la timeline daily/weekly/monthly,
#  il faudrait tout coder à la main. Voir si c'est possible de gérer ça sur pandas directement)
tweet_count_by_day = {}
for tweet in json_tweets['tweets']:
    raw_date = tweet['created_at'][0:10] + tweet['created_at'][25:30]
    formatted_date =  datetime.datetime.strptime(raw_date,"%a %b %d %Y").strftime("%Y-%m-%d")
    if formatted_date in tweet_count_by_day.keys():
        tweet_count_by_day[formatted_date] += 1
    else:
        tweet_count_by_day[formatted_date] = 1
tweet_count_by_day = sorted(tweet_count_by_day.items())
print(sum(t[1] for t in tweet_count_by_day))
print(tweet_count_by_day)

df = pd.DataFrame.from_dict(json_tweets)
#print(df.head(5))
columns=['day','count']
data = []
index = 0

for day,day_count in tweet_count_by_day:
    data.append([day,day_count])
df = pd.DataFrame(data,columns=columns)
#print(df.head(5))
#print(df.info())
# Convert the dataframe index to a datetime index to do time series manipulation
# To do so, turn the 'day' column into a DateTime data type then make it the index of the dataframe
df.day = pd.to_datetime(df.day)
df.set_index('day',inplace=True)
#print(df.head(5))
#print(df.info())

# Plot the time series of the dataframe
df.plot(figsize=(10,7), linewidth=5, fontsize=20)
plt.xlabel('Day', fontsize=20)
plt.show(block=True)

# Detect change of slope
