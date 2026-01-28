# Semantic Vector Search Engine

Embedding-Based Semantic Retrieval and Summarization System

## Overview

Semantic Vector Search Engine is a domain-agnostic system designed to explore and demonstrate how semantic embeddings, vector similarity, and meaning-based ranking work in real-world applications.

The project retrieves documents, represents them as dense vectors using transformer models, and ranks them based on semantic relevance rather than keyword overlap.

Research papers are used only as an example dataset.
The same system can be applied to any long-form text corpus.

## Purpose of the Project

This project was built to gain a practical and architectural understanding of:

* Semantic representations of text

* Dense vector embeddings

* Cosine similarity–based ranking

* End-to-end semantic search pipelines

* Tradeoffs between keyword search and vector search

The focus is on understanding the working principles, not building a domain-specific application.

## Key Features

* Semantic (meaning-based) search instead of keyword matching

* Transformer-based text embeddings

* Vector similarity scoring using cosine similarity

* Sentence-complete, non-truncated summaries

* Parallel document fetching for improved performance

* Clean and minimal web interface

## System Architecture

    User Query
      ↓
    Candidate Document Retrieval
      ↓
    Text Section Extraction
      ↓
    Transformer Embeddings
      ↓
    Cosine Similarity Ranking
      ↓
    Top-K Semantic Results
      ↓
    Sentence-Complete Summary
      ↓
    User Interface



## Project Structure
    .
    ├── app.py
    ├── run_app.py
    ├── semantic_search_engine.py
    ├── pmc_client.py
    ├── embedding_cache.py
    ├── api.py
    ├── evaluation/
    |   ├── run_test.py
    │   ├── baseline_tfidf.py
    │   ├── evaluate_relevance.py
    │   └── benchmark_latency.py
    ├── requirements.txt
    └── README.md


## Domain-Agnostic Design

Although biomedical research papers are used in this implementation, the same system can be applied to other domains such as:

* Wikipedia article search

* HR policy and internal documentation search

* Enterprise knowledge bases

* Legal and compliance document retrieval

* Technical documentation search

Only the data ingestion layer needs to change.

## Technologies Used

* Python

* Sentence-Transformers

* PyTorch

* NumPy

* Streamlit

* FastAPI (optional API layer)

## Running the Project
Install dependencies

    pip install -r requirements.txt

Run the application

    streamlit run app.py

(Optional) Expose the app publicly

    python run_app.py

API Usage (Optional)
Start the API server:

    uvicorn api:app --reload

Example request:

    {
      "query": "semantic document retrieval",
      "top_k": 5
    }

## Future Improvements

* Hybrid retrieval (keyword + vector search)

* Cross-encoder reranking

* Domain-specific embedding fine-tuning

* Persistent vector stores for large-scale deployment
