from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class TfidfSearch:
    def __init__(self, documents):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000
        )
        self.docs = documents
        self.doc_vectors = self.vectorizer.fit_transform(documents)

    def search(self, query, top_k=5):
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.doc_vectors)[0]
        top_indices = np.argsort(scores)[::-1][:top_k]
        return top_indices
