from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN

def build_threads(docs):
    texts = [d["headline"] + " " + d["body"][:200] for d in docs]
    tfidf = TfidfVectorizer(stop_words="english").fit_transform(texts)
    
    clusters = DBSCAN(eps=0.4, min_samples=2).fit_predict(tfidf)
    
    threads = {}
    for doc, cluster_id in zip(docs, clusters):
        if cluster_id == -1: cluster_id = f"single-{doc['doc_id']}"
        threads.setdefault(cluster_id, []).append(doc)
    return threads