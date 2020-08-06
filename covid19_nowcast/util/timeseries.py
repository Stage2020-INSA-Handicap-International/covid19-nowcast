import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import datetime
import ruptures as rpt


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
columns=['day','tweet_count']
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
plt.title('Count of tweets related to the COVID-19 pandemic in Kenya',size=15)
plt.xlabel('Day', fontsize=15)
f1 = plt.figure(1)
f1.show()

# DETECT CHANGE OF SLOPE
# Convert the time series values to a numpy 1D array
points = np.array(df['tweet_count'])
print(points)
# Ruptures package
# Changepoint detection with the Pelt search method, o(N)
model = "rbf"
algo = rpt.Pelt(model = model).fit(points)
result = algo.predict(pen=0.8)
rpt.display(points, result, figsize=(10,7))
plt.title('Change Point Detection : Pelt Search Method')
f2 = plt.figure(2)
f2.show()

plt.show()
'''
# Changepoint detection with the Binary Segmentation search method
model = "l2"
algo = rpt.Binseg(model=model).fit(points)
my_bkps = algo.predict(n_bkps=10)
# show results
rpt.show.display(points, my_bkps, figsize=(10, 7))
plt.title('Change Point Detection: Binary Segmentation Search Method')
f3 = plt.figure(3)
f3.show()

#Changepoint detection with window-based search method
model = "l2"
algo = rpt.Window(width=40, model=model).fit(points)
my_bkps = algo.predict(n_bkps=10)
rpt.show.display(points, my_bkps, figsize=(10, 7))
plt.title('Change Point Detection: Window-Based Search Method')
f4 = plt.figure(4)
f4.show()

#Changepoint detection with dynamic programming search method
model = "l1"
algo = rpt.Dynp(model=model, min_size=3, jump=5).fit(points)
my_bkps = algo.predict(n_bkps=10)
rpt.show.display(points, my_bkps, figsize=(10, 7))
plt.title('Change Point Detection: Dynamic Programming Search Method')
f5 = plt.figure(5)
f5.show()

plt.show()
'''
