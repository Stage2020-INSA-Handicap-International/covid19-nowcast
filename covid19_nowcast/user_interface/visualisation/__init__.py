from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from graphviz import Digraph
def generate_graph():
    pass

def n_gram_graph(texts, n_words=20, min_size=11, max_size=32):
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
    for index,bigram in enumerate(top_n):
        a,b=bigram
        dot.attr('node', color='transparent', fontname="helvetica")
        dot.attr('node',fontsize=str(int(min_size*ratio[a]+max_size*(1-ratio[a]))))
        dot.node(a)
        dot.attr('node',fontsize=str(int(min_size*ratio[b]+max_size*(1-ratio[b]))))
        dot.node(b)
        dot.edge(a,b)
    filename=dot.render()
    return filename
