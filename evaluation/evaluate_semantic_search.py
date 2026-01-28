import numpy as np

from baseline_tfidf import TfidfSearch
from semantic_search_engine import SemanticSearchEngine


# ----------------------------
# Concept-based evaluation queries
# ----------------------------
queries = [
    "conceptual document understanding",
    "context aware text retrieval",
    "dense vector similarity methods",
    "meaning driven information retrieval",
    "semantic representation of text"
]


# ----------------------------
# Load documents (fixed corpus)
# ----------------------------
documents = load_documents()
print(f"Evaluating on {len(documents)} documents")

# ----------------------------
# Initialize engines
# ----------------------------
tfidf_engine = TfidfSearch(documents)
semantic_engine = SemanticSearchEngine()


# ----------------------------
# Manual relevance labels (by meaning)
# ----------------------------
relevance = {
    0: {0, 2},
    1: {1, 3},
    2: {4, 5},
    3: {0, 6},
    4: {2, 7}
}


# ----------------------------
# Metrics
# ----------------------------
def precision_at_k(results, relevant, k=5):
    return len(set(results[:k]) & relevant) / k


def recall_at_k(results, relevant, k=5):
    if not relevant:
        return 0.0
    return len(set(results[:k]) & relevant) / len(relevant)


tfidf_p, semantic_p = [], []
tfidf_r, semantic_r = [], []

# ----------------------------
# Precompute embeddings once
# ----------------------------
doc_embeddings = semantic_engine.embed_texts(documents)

# ----------------------------
# Evaluation loop
# ----------------------------
for i, q in enumerate(queries):
    print(f"\nQuery: {q}")

    # ---- TF-IDF ----
    tfidf_results = tfidf_engine.search(q, top_k=5)
    tfidf_p.append(precision_at_k(tfidf_results, relevance[i]))
    tfidf_r.append(recall_at_k(tfidf_results, relevance[i]))

    # ---- Semantic (larger candidate pool) ----
    query_embedding = semantic_engine.embed_texts([q])[0]
    scores = doc_embeddings @ query_embedding

    # IMPORTANT: rank over more candidates, then cut to top_k
    semantic_results = np.argsort(scores)[::-1][:10]

    semantic_p.append(precision_at_k(semantic_results, relevance[i]))
    semantic_r.append(recall_at_k(semantic_results, relevance[i]))


print("\n============================")
print("TF-IDF Precision@5 :", np.mean(tfidf_p))
print("Semantic Precision@5:", np.mean(semantic_p))
print()
print("TF-IDF Recall@5    :", np.mean(tfidf_r))
print("Semantic Recall@5  :", np.mean(semantic_r))
print("============================")
