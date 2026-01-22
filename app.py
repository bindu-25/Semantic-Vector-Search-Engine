# app.py

import streamlit as st

# ---------------- CACHING ----------------
@st.cache_resource
def get_engine():
    from semantic_search_engine import SemanticSearchEngine
    return SemanticSearchEngine()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Biomedical Research Explorer",
    layout="wide"
)

# ---------------- CENTERED HEADER ----------------
st.markdown(
    """
    <div style="text-align: center;">
        <h1 style="margin-bottom: 0.2em;">Biomedical Research Explorer</h1>
        <p style="color: #b0b0b0; margin-top: 0;">
            Semantic search and summarization of open-access medical research papers
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- INPUTS ----------------
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input(
        "Search query",
        placeholder="e.g. brain cancer, glioblastoma treatment, tumor metabolism"
    )
with col2:
    top_k = st.number_input(
        "Results",
        min_value=1,
        max_value=10,
        value=5
    )

search_btn = st.button("Search")

# ---------------- SEARCH ----------------
if search_btn:
    if not query.strip():
        st.warning("Please enter a search query.")
    else:
        with st.spinner("Searching biomedical literature..."):
            engine = get_engine()
            res = engine.search(query, top_k=top_k)

        results = res.get("results", [])

        st.markdown(f"### Results for “{query}”")

        if not results:
            st.info("No relevant papers found.")
        else:
            for i, r in enumerate(results, start=1):
                relevance_pct = r["score"] * 100

                with st.expander(
                    f"Paper {i} · {r['pmcid']}  —  Relevance: {relevance_pct:.1f}%"
                ):
                    st.markdown("**Summary**")

                    st.text_area(
                        label="",
                        value=r["summary"],
                        height=250
                    )

                    st.markdown(
                        f"[Read full paper on PubMed Central]({r['link']})"
                    )
