# covid19-nowcast-africa
Detect and analyze the spread of COVID-19 in Africa thanks to social networks led by [BETTINGER Matthieu](), [HAFID Salim]() and [SADER Bruno]() for Humanity & Inclusion in collaboration with the Foundation INSA.

# Summary
# Research phase
# Corpus and crawler
// Mentionner qu'on a crée des crawlers mais qu'on n'utilise que l'API officielle pour l'app web
# Volumetric Analysis
# Topic Analysis
# Sentimental Analysis
## English 
For the english sentiment analyser, we decided to use a XLNet ([XLNet: Generalized Autoregressive Pretraining for Language Understanding](https://arxiv.org/abs/1906.08237)). <br>
The XLNet has two major advantages : it outperforms most NLP models (including BERT and RoBERTa) and is easly implementable thanks to transformers (formerly known as pytorch-transformers).<br>
We finetune the model with a preset of labled tweets focused around COVID-19.
## French
For the french sentiment analyser, we decided to use CamemBERT ([CamemBERT: a Tasty French Language Model](https://arxiv.org/abs/1911.03894)). <br>
CamemBERT is the only good performing pretrained language model trained on the French data. It is also easly implementable thanks to transformers (formerly known as pytorch-transformers).<br>
We finetune the model with a preset of labled tweets focused around COVID-19.
# Categorization
## Corpus
In order to categorize text, we needed a large labeled corpus.<br>
To solve our problem, we decide to crawl different news outlets and use their articles categories as labels for our text. <br>
Example : We crawled the New-York Times and sorted our corpus into "World", "U.S.", "Politics", "N.Y.", "Business", "Opinion", "Tech", "Science", "Health", "Sports", "Arts", "Books", "Style" "Food"", "Travel", "Magazine" and "T Magazine".<br>
Out of all the data, we decided to keep only 8 categories that we thought could be of interest ("Politics", "Business", "Tech", "Science", "Health", "Sports", "Food" and "Travel").<br>
## Training
Once our data collected, we use a XLNet for the categorizer. <br>
We train our model on the crawled articles and then finetune it with a preset of categorised tweets focused around COVID-19.<br>
<br>
The categorizer has two major flaws. 
- It only works on English data. An improvement would be training a CamemBERT to categorize French data.
- The training data was cut short due to the lack of computing power. In our case, we trained the model on the 20 most frequent words found in each article. An improvement would be to train the model on the full text.<br>

We believe that for the categorizer a lighter and easier to train model could be used (i.e NBSVM). 

# Cross Analysis
# Web app developement
# Backend
## Server operation
## Collection Manager
## etc
# Frontend
## Used APIs
## Operation and workflows
## Topics
## Graphs
## etc
# Setup and installation
## Weekly Data Collection Automation
### Prerequisites
sudo apt-get install cron
### Setup
#### Data collection
##### Data inputs
A .csv can be used to instruct which data shall be collected.

The format is a list of tuples as follows: 
  Country, Language, Source (opt, default=twitter), Count(opt, default=100/day)
Example:
  France,fr,,200
  India,en,,

##### Data collection script
  collector.sh launches collector.py with a .csv file as argument. This file shall follow the preceding data format.
##### Data collection interface
  collector.py launches /collector POST queries to the server.
  See python collector.py -h output for detailled instructions on its standalone usage.

#### Automation
The preceding files can be orchestrated to be automatically run using cron.
Add a new cron job using:
  crontab -e

Add a new line setting the collection command to be run and its frequency:

Pattern:

<cron-frequency> cd <path-to-script> && ./collector.sh (>> <log-filepath> 2>&1)
  
Example:

@weekly cd ~/Documents/HI/covid19_nowcast_africa/covid19_autocollector && ./collector.sh >> ./collector.log 2>&1
