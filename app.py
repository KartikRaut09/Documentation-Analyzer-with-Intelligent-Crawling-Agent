import streamlit as st

from crawler.crawler import crawl_website
from processing.chunker import chunk_documents
from rag.qa import answer_query
from vectorstore.db import build_vectorstore


st.set_page_config(
    page_title="Documentation Analyzer AI",
    page_icon=":books:",
    layout="wide",
)

st.markdown(
    """
    <style>
        .main-title {
            font-size: 32px;
            font-weight: bold;
        }
        .subtitle {
            color: gray;
            margin-bottom: 20px;
        }
        .stButton button {
            width: 100%;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">Documentation Analyzer AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Ask questions from any documentation or knowledge base using AI</div>',
    unsafe_allow_html=True,
)

if "history" not in st.session_state:
    st.session_state.history = []

if "kb_ready" not in st.session_state:
    st.session_state.kb_ready = False

with st.sidebar:
    st.header("Controls")
    seed_url = st.text_input("Documentation URL")
    crawl_limit = st.slider("Max Pages to Crawl", 1, 50, 10)

    if st.button("Crawl and Build Knowledge Base"):
        if not seed_url.strip():
            st.warning("Please enter a valid URL.")
        else:
            try:
                with st.spinner("Crawling and processing..."):
                    docs = crawl_website(seed_url, max_pages=crawl_limit)
                    if not docs:
                        raise ValueError("No pages were crawled. Check the URL and try again.")

                    chunks = chunk_documents(docs)
                    build_vectorstore(chunks)

                st.session_state.kb_ready = True
                st.success("Knowledge base is ready.")
            except Exception as e:
                st.session_state.kb_ready = False
                st.error(f"Failed to build knowledge base: {e}")

    st.markdown("---")
    st.markdown("**System Status**")

    if st.session_state.kb_ready:
        st.success("Knowledge base loaded")
    else:
        st.info("No knowledge base")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Ask Questions")
    user_query = st.text_input("Enter your question")

    if st.button("Get Answer"):
        if not st.session_state.kb_ready:
            st.warning("Build a knowledge base first.")
        elif not user_query.strip():
            st.warning("Enter a valid question.")
        else:
            try:
                with st.spinner("Generating answer..."):
                    answer, sources = answer_query(user_query)

                st.session_state.history.append(
                    {"question": user_query, "answer": answer, "sources": sources}
                )
            except Exception as e:
                st.error(f"Failed to answer question: {e}")

with col1:
    for chat in reversed(st.session_state.history):
        with st.chat_message("user"):
            st.write(chat["question"])

        with st.chat_message("assistant"):
            st.write(chat["answer"])

            with st.expander("Sources"):
                for src in set(chat["sources"]):
                    st.write(src)

with col2:
    st.subheader("Session Info")
    st.write(f"Questions Asked: **{len(st.session_state.history)}**")

    if st.button("Clear Chat"):
        st.session_state.history = []
        st.rerun()

    st.markdown("---")
    st.subheader("How It Works")
    st.markdown(
        """
        1. Crawl documentation/site
        2. Clean and chunk content
        3. Convert chunks to embeddings
        4. Store in vector database
        5. Retrieve and generate answers
        """
    )

    st.markdown("---")
    st.subheader("Features")
    st.markdown(
        """
        - Intelligent crawling
        - Semantic search
        - Metadata-aware retrieval
        - Citation grounding
        - RAG-based responses
        """
    )
