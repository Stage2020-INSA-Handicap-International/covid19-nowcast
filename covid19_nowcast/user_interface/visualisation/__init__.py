from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from graphviz import Digraph
from collections import Counter

def generate_graph():
    pass

def n_gram_graph(texts, alarm_words, n_words=20, min_size=11, max_size=32):
    if texts!=[]:
        tfidf= TfidfVectorizer(ngram_range=(2,2))
        graph = tfidf.fit_transform(texts[:1000])
        feature_array = np.array(tfidf.get_feature_names())
        tfidf_sorting = np.argsort(graph.toarray()).flatten()[::-1]
        top_n = feature_array[tfidf_sorting][:n_words]
        top_n=[ng.split(" ") for ng in top_n]
    else:
        top_n=[]
    dot=Digraph("N-gram cloud",format="png",filename="ngram_cloud")
    ratio={}
    for index,bigram in enumerate(top_n):
        a,b=bigram
        ratio[a]=ratio.get(a,[])
        ratio[a].append(index)
        ratio[b]=ratio.get(b,[])
        ratio[b].append(index)
    ratio={key:np.average(value)/len(top_n) for key,value in ratio.items()}

    edges=[]
    for index,bigram in enumerate(top_n):
        a,b=bigram
        dot.attr('node', color='transparent', fontname="helvetica")
        dot.attr('node',fontsize=str(int(min_size*ratio[a]+max_size*(1-ratio[a]))))
        if a in alarm_words:
            dot.attr('node',fontcolor="red")
            dot.node(a)
        else:
            dot.attr('node',fontcolor="black")
            dot.node(a)
        dot.attr('node',fontsize=str(int(min_size*ratio[b]+max_size*(1-ratio[b]))))
        if b in alarm_words:
            dot.attr('node',fontcolor="red")
            dot.node(b)
        else:
            dot.attr('node',fontcolor="black")
            dot.node(b)
        if (a,b) not in edges:
            dot.edge(a,b)
            edges.append((a,b))
    filename=dot.render()
    return filename

def alarm_graph(texts, alarm_words, nb_surround_words=5, min_size=11, max_size=32):
    if texts!=[]:
        tfidf= TfidfVectorizer(ngram_range=(2,2),use_idf=False)
        graph = tfidf.fit_transform(texts[:1000])
        feature_array = np.array(tfidf.get_feature_names())
        tfidf_sorting = np.argsort(graph.toarray()).flatten()[::-1]

        sorted_bigrams = feature_array[tfidf_sorting]
        sorted_bigrams=[ng.split(" ") for ng in sorted_bigrams]
        alarm_bigrams=[]
        for a,b in sorted_bigrams:
            if a in alarm_words or b in alarm_words:
                alarm_bigrams.append([a,b])
    else:
        alarm_bigrams=[]

    surround_counter = Counter()
    top_n=[]
    for a,b in alarm_bigrams:
        if a in alarm_words:
            if (a,b) not in top_n:
                if surround_counter[a]<nb_surround_words:
                    top_n.append((a,b))
                surround_counter[a]+=1
        if b in alarm_words:
            if (a,b) not in top_n:
                if surround_counter[b]<nb_surround_words:
                    top_n.append((a,b))
                surround_counter[b]+=1

    dot=Digraph("N-gram cloud",format="png",filename="ngram_cloud")
    ratio={}
    for index,bigram in enumerate(top_n):
        a,b=bigram
        ratio[a]=ratio.get(a,[])
        ratio[a].append(index)
        ratio[b]=ratio.get(b,[])
        ratio[b].append(index)
    ratio={key:np.average(value)/len(top_n) for key,value in ratio.items()}
    print(alarm_words)
    for index,bigram in enumerate(top_n):
        a,b=bigram
        dot.attr('node', color='transparent', fontname="helvetica")
        dot.attr('node',fontsize=str(int(min_size*ratio[a]+max_size*(1-ratio[a]))))
        if a in alarm_words:
            dot.attr('node',fontcolor="red")
            dot.node(a)
        else:
            dot.attr('node',fontcolor="black")
            dot.node(a)
        dot.attr('node',fontsize=str(int(min_size*ratio[b]+max_size*(1-ratio[b]))))
        if b in alarm_words:
            dot.attr('node',fontcolor="red")
            dot.node(b)
        else:
            dot.attr('node',fontcolor="black")
            dot.node(b)
        dot.edge(a,b)
    filename=dot.render()
    return filename
