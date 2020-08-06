from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import json
from datetime import datetime

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from covid19_nowcast.streaming.collection import covid19_api
from covid19_nowcast import util, analysis
from covid19_nowcast.user_interface import visualisation
def index(request):
    return render_to_response('index.html')

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
                "date_from":str in %Y-%m-%dT%H:%M:%SZ format,
                "date_to":str in %Y-%m-%dT%H:%M:%SZ format
            }
        """
        params=json.loads(request.body)

        # Sanity checks
        date_keys=["date_from","date_to"]
        keys=["country","source"]
        keys.extend(date_keys)
        try:
            for key in keys:
                check_missing(key,params.keys())
                check_type(key, params[key], str)

            available_countries=covid19_api.get_countries()
            found_country=False
            for country in available_countries:
                if params["country"] in country.values():
                    params["country"]=country["Slug"]
                    found_country=True
            assert found_country, "{} is not an available country for analyses".format(params["country"])

            available_sources=["twitter"]
            assert params["source"] in available_sources, "source=\"{}\" not in available sources={}".format(params["source"], available_sources)

            def test_date(date):
                try:
                    datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
                except ValueError as e:
                    raise(AssertionError(e))
                return False

            for date_key in date_keys:
                test_date(params[date_key])
        except AssertionError as e:
            return HttpResponse(json.dumps({"request":params},ensure_ascii=False),status=400, reason="BAD REQUEST: "+str(e))
        
        # Request processing
        if not all(key in request.session and params[key]==request.session[key] for key in keys):
            request.session.flush() # invalidate the entire session because the dataset is different
            # collect_sts_data(params["country"], params["source"], params["date_from"], params["date_to"])
            tweets=util.import_params("../output/topics_india_tw0.json")["tweets"]
            request.session["data"]=tweets

        # Session management
        request.session["country"]=params["country"]
        request.session["source"]=params["source"]
        request.session["date_from"]=params["date_from"]
        request.session["date_to"]=params["date_to"]

        response=HttpResponse(json.dumps({"request":params},ensure_ascii=False),status=501)
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
        topics=None
        if request.session.get("topics",None) is not None \
                and request.session.get("modified_category_topics",False) == False \
                and request.session.get("nb_topics",-1)==params["nb_topics"]:
            topics=request.session["topics"]
        else:
            tweets=request.session["data"]
            tweets,topics=analysis.topics.topicalize_tweets(tweets, params["nb_topics"])
            request.session["modified_topics"]=True
            request.session["data"]=tweets

        # Session management
        request.session["nb_topics"]=params["nb_topics"]

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
            "nb_examples":int>0
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

        except AssertionError as e:
            return HttpResponse(json.dumps({"request":params},ensure_ascii=False),status=400, reason="BAD REQUEST: "+str(e))

        # Request processing
        tweets=request.session["data"]
        topic_indices=[t["topic_id"] for t in tweets]
        topics=request.session["topics"]
        examples=analysis.topics.top_topic_tweets_by_proba(tweets,topic_indices,topics, params["nb_examples"])[params["topic"]]["top_tweets"]
        examples=[e["full_text"] for e in examples]
        # Session management
        request.session["examples"]=examples
        request.session["topic"]=params["topic"]
        request.session["nb_examples"]=params["nb_examples"]
        
        response=HttpResponse(json.dumps({"examples":examples,"request":params},ensure_ascii=False),status=200)
        return response

class GraphAnalysisView (View):
    @csrf_exempt
    def post(self, request):
        """
            {
                "sentiments":{"positive":bool, "negative":bool, "neutral":bool},
                "cases":{"enabled":bool, "rolling":bool},
                "trends":bool,
                "topic":int in topic classifier classes,
                "period":str in ["day","week","month"]
            }
        """
        params=json.loads(request.body)

        # Sanity checks
        try:
            assert request.session.get("data",None) is not None, "Data hasn't been collected yet"
            assert request.session.get("category_data",None) is not None, "Data hasn't been categorized yet"
            assert request.session.get("topics", None) is not None or params.get("topic","All") == "All", "Topic analysis hasn't been executed yet, but topic selection was requested"
        except AssertionError as e:
            return HttpResponse(json.dumps({"request":params},ensure_ascii=False),status=409, reason="Conflict: "+str(e))

        keys={"sentiments":dict, "cases":dict, "trends":bool, "topic":str, "period":str}
        try:
            for key, t in keys.items():
                check_missing(key, params.keys())
                check_type(key, params[key], t)

            items={
                    "sentiments":["positive", "negative", "neutral"],
                    "cases":["enabled","rolling"]
                }
            for key, value in items.items():
                for val_key in value:
                    check_missing(val_key, params[key].keys())
                    check_type(value,params[key][val_key], bool)

            assert params["period"] in ["day","week","month"]

            # <!> Check topic_id is in classifier classes
        except AssertionError as e:
            return HttpResponse(json.dumps({"request":params},ensure_ascii=False),status=400, reason="BAD REQUEST: "+str(e))

        # Request processing
        graph_img=None
        if request.session.get("graph",None) is not None \
                and request.session.get("modified_category_graph",False)==False \
                and request.session.get("modified_topics",False)==False \
                and all([key in request.session.keys() and params[key]==request.session[key] for key in keys.keys()]):
            graph_img=request.session["graph"]
        else:
            graph_img=None # <!> execute function 
            
        # Session management
        request.session["sentiments"]=params["sentiments"]
        request.session["cases"]=params["cases"]
        request.session["trends"]=params["trends"]
        request.session["graph_topic"]=params["topic"]
        request.session["period"]=params["period"]

        request.session["modified_category_graph"]=False
        request.session["modified_topics"]=False
        request.session["graph"]=graph_img

        #response=HttpResponse(graph_img, content_type="image/jpeg")
        response=HttpResponse(json.dumps({"request":params},ensure_ascii=False),status=501)
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

            available_categories=["Unknown"] # <!> Replace with real categories from classifier
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
        response=HttpResponse(json.dumps({"request":params},ensure_ascii=False),status=501)
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
    response = str(request.session.items())
    return HttpResponse(response)

def delete_session(request):
    try:
        keys=[k for k in request.session.keys()]
        for key in keys:
            del request.session[key]
    except KeyError:
        pass
    return HttpResponse("<h1>dataflair<br>Session Data cleared</h1>")
