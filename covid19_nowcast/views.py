from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import base64
import copy
import json
from datetime import datetime, timedelta

#from django.shortcuts import render_to_response, redirect
from django.shortcuts import render
from django.template import RequestContext

from covid19_nowcast.streaming.collection import covid19_api
from covid19_nowcast import util, analysis
from covid19_nowcast.user_interface import visualisation
from covid19_nowcast.streaming import CollectionManager
from covid19_nowcast.streaming import storage
from covid19_nowcast.analysis import AnalysisManager
from covid19_nowcast.streaming.preparation import PreprocessManager
from covid19_nowcast.user_interface import visualisation
from covid19_nowcast.streaming.collection import covid19_api

def check_type(key, value, t):
    assert type(value) is t, "{} = {} is not {}".format(key,value,t.__name__)

def check_missing(key, keys):
    assert key in keys, "\"{}\" is missing".format(key)

class CollectorView (View):
    @csrf_exempt
    def post(self, request):
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
        params=json.loads(request.body)

        # Sanity checks
        date_keys=["date_from","date_to"]
        keys=["country","source","lang"]
        keys.extend(date_keys)
        try:
            for key in keys:
                check_missing(key,params.keys())
                check_type(key, params[key], str)

            key="lang"
            available_languages=["fr","en"]
            assert params[key] in available_languages, "lang=\"{}\" not in available languages={}".format(params["lang"], available_languages)
            available_countries=covid19_api.get_countries()

            key="count"
            check_missing(key,params.keys())
            check_type(key, params[key], int)
            assert params[key]>0, "\"{}\" is not >0".format(key)

            found_country=False
            for country in available_countries:
                if params["country"] in country.values():
                    params["country"]=country
                    found_country=True
            assert found_country, "{} is not an available country for analyses".format(params["country"])

            available_sources=["twitter"]
            assert params["source"] in available_sources, "source=\"{}\" not in available sources={}".format(params["source"], available_sources)

            def test_date(date):
                try:
                    datetime.strptime(date, '%Y-%m-%d')
                except ValueError as e:
                    raise(AssertionError(e))
                return date

            for date_key in date_keys:
                test_date(params[date_key])

            mem_date_to=copy.copy(params["date_to"])
            params["date_to"]=datetime.strftime(datetime.strptime(params["date_to"], '%Y-%m-%d')+timedelta(days=1),'%Y-%m-%d')
            assert params["date_from"] < params["date_to"], "beginning date {} is later than end {}".format(params["date_from"],mem_date_to)
        except AssertionError as e:
            return HttpResponse(json.dumps({"request":params},ensure_ascii=False),status=400, reason="BAD REQUEST: "+str(e))
        
        # Request processing
        if not all(key in request.session and params[key]==request.session[key] for key in keys):
            request.session.flush() # invalidate the entire session because the dataset is different
            tweets=CollectionManager.collect_sts_data(params["country"], params["source"], params["lang"], params["date_from"], params["date_to"], params["count"])
            tweets=PreprocessManager.preprocess(tweets,params["country"]["Country"],params["lang"])
            tweets=AnalysisManager.analyze(tweets,5)
            
            request.session["data"]=tweets

        # Session management
        request.session["country"]=params["country"]
        request.session["source"]=params["source"]
        request.session["date_from"]=params["date_from"]
        request.session["date_to"]=params["date_to"]
        request.session["lang"]=params["lang"]
        request.session["count"]=params["count"]


        response=HttpResponse(json.dumps({"count":len(request.session["data"]),"request":params},ensure_ascii=False),status=200)

        return response

class TopicAnalysisView (View):
    @csrf_exempt
    def post(self, request):
        """
        {
            "nb_topics":int>0
        }
        """
        params=json.loads(request.body)

        # Sanity checks
        try:
            assert request.session.get("data",None) is not None, "Data hasn't been collected yet"
            assert request.session.get("category_data",None) is not None, "Data hasn't been categorized yet"
        except AssertionError as e:
            return HttpResponse(json.dumps({"request":params},ensure_ascii=False),status=409, reason="Conflict: "+str(e))

        try:
            key="nb_topics"
            check_missing(key, params.keys())
            check_type(key,params[key],int)
            assert params[key]>0, "\"{}\" is not >0".format(key)
        except AssertionError as e:
            return HttpResponse(json.dumps({"request":params},ensure_ascii=False),status=400, reason="BAD REQUEST: "+str(e))
            
        # Request processing
        topics=[]
        if request.session.get("topics",None) is not None \
                and request.session.get("modified_category_topics",False) == False \
                and request.session.get("nb_topics",-1)==params["nb_topics"]:
            topics=request.session["topics"]
        else:
            tweets=request.session["category_data"]
            if tweets!=[]:
                tweets,topics=analysis.topics.topicalize_tweets(tweets, params["nb_topics"])
                alarm_words=storage.get_alarm_words()
                topics=analysis.topics.tag_alarm_words(topics, alarm_words)
            request.session["modified_topics"]=True
            request.session["category_data"]=tweets

        # Session management
        request.session["nb_topics"]=len(topics)

        request.session["topics"]=topics
        request.session["modified_category_topics"]=False

        response=HttpResponse(json.dumps({"topics":topics,"request":params},ensure_ascii=False),status=200)
        return response

class TopicExamplesView (View):
    @csrf_exempt
    def post(self, request):
        """
        {
            "topic":int>=0 and <nb_topics,
            "nb_examples":int>0,
            "graph":{
                "nb_words":int,
                "min_font_size":int,
                "max_font_size":int,
                "type":str in ["alarm","relevant"]
            }
        }
        """
        params=json.loads(request.body)

        # Sanity checks
        try:
            assert request.session.get("topics",None) is not None, "Topic analysis has not been executed yet"
            assert request.session.get("nb_topics",None) is not None, "Topic analysis has not been executed yet"
            assert request.session.get("data",None) is not None, "Data hasn't been collected yet"
            assert request.session.get("category_data",None) is not None, "Data hasn't been categorized yet"
        except AssertionError as e:
            return HttpResponse(json.dumps({"request":params},ensure_ascii=False),status=409, reason="Conflict: "+str(e))

        try:
            key="nb_examples"
            check_missing(key, params.keys())
            check_type(key,params[key],int)
            assert params[key]>0, "\"{}\" is not >0".format(key)

            key="topic"
            check_missing(key, params.keys())
            check_type(key,params[key],int)
            assert params[key]>=0, "\"{}\" is not >=0".format(key)
            assert params["topic"] < request.session["nb_topics"], "Topic index {} is out of bounds ({} topics)".format(params["topic"],request.session["nb_topics"])

            key="graph"
            check_missing(key, params.keys())
            check_type(key,params[key],dict)
            subkeys=["nb_words","min_font_size","max_font_size"]
            for k in subkeys:
                check_missing(k, params[key].keys())
                check_type(k,params[key][k],int)
                assert params[key][k]>0, "\"{}__{}\" is not >0".format(key,k)

            subkey="type"
            check_missing(subkey, params[key].keys())
            available_graph_types=["alarm","relevant"]
            check_type(subkey,params[key][subkey],str)
            assert params[key][subkey] in available_graph_types, "Unknown graph type {}: type not in {}".format(subkey,available_graph_types)
        except AssertionError as e:
            return HttpResponse(json.dumps({"request":params},ensure_ascii=False),status=400, reason="BAD REQUEST: "+str(e))

        # Request processing
        tweets=request.session["category_data"]
        topic_indices=[t["topic_id"] for t in tweets]
        topics=request.session["topics"]
        examples=analysis.topics.top_topic_tweets_by_proba(tweets,topic_indices,[list(topic.keys()) for topic in topics], params["nb_examples"])[params["topic"]]["top_tweets"]
        examples=[e["full_text"] for e in examples]
        topic_texts=[t["preproc_text"] for t in tweets if t["topic_id"]==params["topic"]]
        alarm_words=storage.get_alarm_words()
        if params["graph"]["type"]=="relevant":
            graph=visualisation.n_gram_graph(topic_texts,alarm_words,params["graph"]["nb_words"],params["graph"]["min_font_size"],params["graph"]["max_font_size"])
        elif params["graph"]["type"]=="alarm":
            graph=visualisation.alarm_graph(topic_texts,alarm_words,params["graph"]["nb_words"],params["graph"]["min_font_size"],params["graph"]["max_font_size"])
        with open(graph, "rb") as img_file:
            graph = str(base64.b64encode(img_file.read()))[2:-1]
        
        # Session management
        request.session["examples"]=examples
        request.session["topic"]=params["topic"]
        request.session["nb_examples"]=params["nb_examples"]
        
        response=HttpResponse(json.dumps({"graph":graph,"examples":examples,"request":params},ensure_ascii=False),status=200)
        return response

class GraphAnalysisView (View):
    @csrf_exempt
    def post(self, request):
        """
            {
                "topic":{"all":bool,"topic_id":int<nb_topics and >=0}
            }
        """
        params=json.loads(request.body)

        # Sanity checks
        try:
            assert request.session.get("data",None) is not None, "Data hasn't been collected yet"
            assert request.session.get("category_data",None) is not None, "Data hasn't been categorized yet"
            assert request.session.get("topics", None) is not None or params.get("topic",{"all":True})["all"] == True, "Topic analysis hasn't been executed yet, but topic selection was requested"
        except AssertionError as e:
            return HttpResponse(json.dumps({"request":params},ensure_ascii=False),status=409, reason="Conflict: "+str(e))

        keys={"topic":dict}
        try:
            for key, t in keys.items():
                check_missing(key, params.keys())
                check_type(key, params[key], t)

            key="topic"
            subkeys={"all":bool,"topic_id":int}
            for k,t in subkeys.items():
                check_missing(k, params[key].keys())
                check_type(k,params[key][k],t)
            if params["topic"]["all"]==False:
                assert params["topic"]["topic_id"] >= 0, "Topic index {} is out of bounds (should be >=0)".format(params["topic"]["topic_id"])
                assert params["topic"]["topic_id"] < request.session["nb_topics"], "Topic index {} is out of bounds ({} topics)".format(params["topic"]["topic_id"],request.session["nb_topics"])
        except AssertionError as e:
            return HttpResponse(json.dumps({"request":params},ensure_ascii=False),status=400, reason="BAD REQUEST: "+str(e))

        # Request processing
        graph_data=None
        keys={"topic":"graph_topic"}
        if request.session.get("graph_data",None) is not None \
                and request.session.get("modified_category_graph",False)==False \
                and request.session.get("modified_topics",False)==False \
                and all([sess_key in request.session.keys() and params[key]==request.session[sess_key] for key, sess_key in keys.items()]):
            graph_data=request.session["graph_data"]
        else:
            if params["topic"]["all"]==True:
                texts_data=request.session["category_data"]
            else:
                texts_data=[t for t in request.session["category_data"] if t["topic_id"]==params["topic"]["topic_id"]]
            texts_data=[{k:v for k,v in t.items() if k in ["created_at","sentiment"]} for t in texts_data]
            cases_data=covid19_api.get_countries_info([request.session["country"]["Slug"]],request.session["date_from"]+"T00:00:00Z",request.session["date_to"]+"T00:00:00Z")[request.session["country"]["Slug"]]
            graph_data={"data":texts_data,"cases":cases_data}
            
        # Session management
        request.session["graph_topic"]=params["topic"]

        request.session["modified_category_graph"]=False
        request.session["modified_topics"]=False
        request.session["graph_data"]=graph_data

        #response=HttpResponse(graph_data, content_type="image/jpeg")
        response=HttpResponse(json.dumps({**graph_data},ensure_ascii=False),status=200)
        return response

class CategoryView (View):
    @csrf_exempt
    def post(self, request):
        """
            {
                "category":str in category classifier classes
            }
        """
        params=json.loads(request.body)

        # Sanity checks
        try:
            assert request.session.get("data",None) is not None, "Data hasn't been collected yet"
        except AssertionError as e:
            return HttpResponse(json.dumps({"request":params},ensure_ascii=False),status=409, reason="Conflict: "+str(e))

        try:
            key="category"
            check_missing(key, params.keys())
            check_type(key,params[key],str)

            available_categories=["All", "Business", "Food", "Health", "Politics", "Science", "Sports", "Tech", "Travel"]

            assert params[key] in available_categories, "{} category is not known".format(params[key])
        except AssertionError as e:
            return HttpResponse(json.dumps({"request":params},ensure_ascii=False),status=400, reason="BAD REQUEST: "+str(e))

        # Session management
        if "category" not in request.session.keys() or request.session["category"] != params["category"]:
            if params["category"]=="All":
                request.session["category_data"]=request.session["data"]
            else:
                request.session["category_data"]=[d for d in request.session["data"] if d["category"]==params["category"]]
            request.session["category"]=params["category"]
            request.session["modified_category_graph"]=True
            request.session["modified_category_topics"]=True
        response=HttpResponse(json.dumps({"count":len(request.session["category_data"]),"request":params},ensure_ascii=False),status=200)
        return response

def cookie_session(request):
    request.session.set_test_cookie()
    return HttpResponse("<h1>dataflair</h1>")

def cookie_delete(request):
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        response = HttpResponse("dataflair<br> cookie created")
    else:
        response = HttpResponse("Dataflair <br> Your browser does not accept cookies")
    return response

def create_session(request):
    request.session['name'] = 'username'
    request.session['password'] = 'password123'
    return HttpResponse("<h1>dataflair<br> the session is set</h1>")
def access_session(request):
    #request.session['test'] = 'item'
    response = str(request.session.items())
    #print("access_session"+response)
    return HttpResponse(response)

def delete_session(request):
    try:
        keys=[k for k in request.session.keys()]
        for key in keys:
            del request.session[key]
    except KeyError:
        pass
    return HttpResponse("<h1>dataflair<br>Session Data cleared</h1>")
