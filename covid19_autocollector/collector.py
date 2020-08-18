import requests

url = 'http://192.168.1.14:8000/collector/'

"""
    {
        "country":str a country which has an entry in the covid19 api,
        "source":str in ["twitter"],
        "lang":str in ["fr","en"],
        "date_from":str in %Y-%m-%d format,
        "date_to":str in %Y-%m-%d format,
        "count":int>0
    }
"""
import json
from argparse import ArgumentParser
from datetime import datetime, timedelta
import pandas as pd
today = datetime.strftime(datetime.today(),"%Y-%m-%d")
today_last_week = datetime.strftime(datetime.today()-timedelta(days=7),"%Y-%m-%d")

parser = ArgumentParser()
parser.add_argument("-f", "--file",dest='filepath', default="",help="File to use for data collection parameters",type=str)
parser.add_argument("-b", "--begin",dest='date_from', default=today_last_week,help="YYYY-mm-dd date. First day to collect",type=str)
parser.add_argument("-e", "--end",dest='date_to', default=today, help="YYYY-mm-dd date. Last day to collect",type=str)
parser.add_argument('-c', "--countries", dest='countries', help='Countries whose data is to be collected', nargs='+',type=str)
parser.add_argument('-l', "--lang", dest='languages', default=["en"], help='Languages in which data shall be collected', nargs='+',type=str)
parser.add_argument('-s', "--source", dest='sources', default=["twitter"], help='Sources in which data shall be collected', nargs='+',type=str)
parser.add_argument('-n', type=int, default=-1, help="Amount of texts to collect",dest='count')
args = parser.parse_args()

if args.count==-1:
    args.count=100*(datetime.strptime(args.date_to,"%Y-%m-%d")-datetime.strptime(args.date_from,"%Y-%m-%d")).days
if args.filepath!="":
    with open(args.filepath,"r") as file:
        params=pd.read_csv(file)
        params["Source"]=params["Source"].fillna("twitter")
        params["Count"]=params["Count"].fillna(100*(datetime.strptime(args.date_to,"%Y-%m-%d")-datetime.strptime(args.date_from,"%Y-%m-%d")).days)
        for req in params.itertuples():
            obj={
                "country":req[1],
                "source":req[3],
                "lang":req[2],
                "date_from":args.date_from,
                "date_to":args.date_to,
                "count":req[4]
            }
            print(obj)
            x = requests.post(url, data = json.dumps(obj))

            print(x.text)
else:
    for country in args.countries:
        for lang in args.languages:
            for source in args.sources:
                obj={
                    "country":country,
                    "source":source,
                    "lang":lang,
                    "date_from":args.date_from,
                    "date_to":args.date_to,
                    "count":args.count
                }
                print(obj)
                x = requests.post(url, data = json.dumps(obj))

                print(x.text)