import time
import numpy as np

queries = [
    "semantic document retrieval",
    "vector search engine",
    "transformer embeddings",
] * 10  # repeat for stability

latencies = []

for q in queries:
    start = time.time()
    semantic_engine.search(q, top_k=5)
    latencies.append(time.time() - start)

print("Average query latency:", np.mean(latencies))
