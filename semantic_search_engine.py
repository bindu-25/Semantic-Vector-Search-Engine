# semantic_search_engine.py
"""
Semantic Search Engine for Biomedical Literature (PMC)

Responsibilities:
- Retrieve live open-access PMC articles via pmc_client
- Encode article sections using transformer embeddings
- Rank sections using cosine similarity
- Generate complete sentence, meaningful summaries

"""

from datetime import datetime, timezone
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

from sentence_transformers import SentenceTransformer

from pmc_client import search_pmc, fetch_pmc_xml, extract_sections


class SemanticSearchEngine:
    """
    Embedding-based semantic search engine over live PMC content.
    """

    def __init__(self):
        # Core embedding model (fast + high quality)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    # ---------------- EMBEDDING ----------------
    def _embed(self, texts: List[str]):
        """
        Encode texts into normalized embedding vectors.
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        norms = (embeddings ** 2).sum(axis=1, keepdims=True) ** 0.5
        return embeddings / norms
    
     # ---------------- PUBLIC EMBEDDING API ----------------
    def embed_texts(self, texts: List[str]):
        """
        Public helper for evaluation and benchmarking.
        Uses the exact same embedding logic as production search.
        """
        return self._embed(texts)

    # ---------------- SUMMARY BUILDER ----------------
    def _build_full_sentence_summary(
        self,
        text: str,
        min_chars: int = 800,
        max_chars: int = 1500
    ) -> str:
        """
        Build a summary using ONLY complete sentences.
        Stops only at sentence boundaries.
        """

        if not text:
            return ""

        sentences = re.split(r'(?<=[.!?])\s+', text.strip())

        summary_parts = []
        total_len = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            summary_parts.append(sentence)
            total_len += len(sentence)

            # Stop after reaching a meaningful length,
            # but only at a sentence boundary
            if total_len >= min_chars:
                break
            if total_len >= max_chars:
                break

        return " ".join(summary_parts)

    # ---------------- FETCH + EXTRACT ----------------
    def _fetch_and_extract(self, pmcid: str) -> List[Dict]:
        """
        Fetch PMC XML and extract usable text sections.
        Designed for parallel execution.
        """
        documents = []
        try:
            root = fetch_pmc_xml(pmcid)
            for section, text in extract_sections(root):
                if text and len(text.strip()) > 200:
                    documents.append({
                        "pmcid": pmcid,
                        "section": section,
                        "text": text
                    })
        except Exception:
            return []

        return documents

    # ---------------- SEARCH ----------------
    def search(self, query: str, top_k: int = 5) -> Dict:
        """
        Perform semantic search over live PMC articles.

        Returns:
        {
            "query": str,
            "retrieved_at": ISO timestamp,
            "results": [
                {
                    "pmcid": str,
                    "section": str,
                    "score": float,
                    "summary": str,
                    "link": str
                }
            ]
        }
        """

        pmcids = search_pmc(query, max_papers=top_k * 2)

        documents = []

        # Parallel network fetching (I/O optimized)
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(self._fetch_and_extract, pmcid)
                for pmcid in pmcids
            ]
            for future in as_completed(futures):
                documents.extend(future.result())

        if not documents:
            return {
                "query": query,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "results": []
            }

        # ---------------- EMBEDDINGS (CORE LOGIC) ----------------
        doc_texts = [doc["text"] for doc in documents]
        doc_embeddings = self._embed(doc_texts)

        query_embedding = self._embed([query])[0]
        scores = doc_embeddings @ query_embedding

        ranked = sorted(
            zip(scores, documents),
            key=lambda x: -x[0]
        )[:top_k]

        results = []
        for score, doc in ranked:
            summary = self._build_full_sentence_summary(doc["text"])

            results.append({
                "pmcid": doc["pmcid"],
                "section": doc["section"],
                "score": float(score),
                "summary": summary,
                "link": f"https://pmc.ncbi.nlm.nih.gov/articles/{doc['pmcid']}/"
            })

        return {
            "query": query,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "results": results
        }
