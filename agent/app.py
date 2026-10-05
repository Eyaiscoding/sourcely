"""
Sourcely - Kubernetes Documentation Q&A Agent

A minimal Streamlit chat interface for querying Kubernetes documentation
using RAG (Retrieval-Augmented Generation) with LanceDB and Ollama (local LLM).

Week 1: Basic retrieval and generation, no citations or guardrails yet.
"""

import os
import sys
import streamlit as st
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.config import LANCEDB_PATH, OLLAMA_MODEL, OLLAMA_BASE_URL

# Import dependencies
try:
    import lancedb
    from sentence_transformers import SentenceTransformer
    import requests
except ImportError as e:
    st.error(f"Missing dependency: {e}. Please run: pip install -r requirements.txt")
    st.stop()


# Page configuration
st.set_page_config(
    page_title="Sourcely - Kubernetes Q&A",
    page_icon="🔍",
    layout="centered"
)


@st.cache_resource
def load_embedding_model():
    """Load the sentence transformer model (cached)."""
    return SentenceTransformer('all-MiniLM-L6-v2')


@st.cache_resource
def load_lancedb_table():
    """Load the LanceDB table (cached)."""
    if not LANCEDB_PATH or not os.path.exists(LANCEDB_PATH):
        st.error(f"LanceDB not found at: {LANCEDB_PATH}. Please run the ingestion pipeline first.")
        st.stop()
    
    try:
        db = lancedb.connect(LANCEDB_PATH)
        table = db.open_table("kubernetes_docs")
        return table
    except Exception as e:
        st.error(f"Error loading LanceDB table: {e}")
        st.stop()


def retrieve_chunks(query: str, top_k: int = 5):
    """
    Retrieve the most relevant chunks from LanceDB.
    
    Args:
        query: User question
        top_k: Number of chunks to retrieve
    
    Returns:
        List of relevant chunks with metadata
    """
    # Generate query embedding
    embedding_model = load_embedding_model()
    query_embedding = embedding_model.encode(query).tolist()
    
    # Search LanceDB
    table = load_lancedb_table()
    results = table.search(query_embedding).limit(top_k).to_list()
    
    return results


def generate_answer(query: str, chunks: list) -> str:
    """
    Generate an answer using Ollama (local LLM).
    
    Args:
        query: User question
        chunks: Retrieved context chunks
    
    Returns:
        Generated answer from Ollama
    """
    # Construct context from retrieved chunks
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        text = chunk.get('text', '')
        source_url = chunk.get('source_url', 'Unknown')
        context_parts.append(f"[Context {i} from {source_url}]\n{text}\n")
    
    context = "\n".join(context_parts)
    
    # Construct prompt
    prompt = f"""You are a helpful assistant that answers questions about Kubernetes documentation.

Use the following context to answer the user's question. If the context doesn't contain enough information, say so.

CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""
    
    # Call Ollama API
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"ERROR: Ollama returned status {response.status_code}. Make sure Ollama is running."
    except requests.exceptions.ConnectionError:
        return "ERROR: Cannot connect to Ollama. Please install and start Ollama: https://ollama.ai"
    except Exception as e:
        return f"ERROR: Failed to generate answer: {str(e)}"


# Main UI
st.title("🔍 Sourcely")
st.caption("Kubernetes Documentation Q&A Agent - Week 1")

st.markdown("""
Ask questions about Kubernetes! This system retrieves relevant documentation 
and uses Ollama (local LLM) to generate answers.

**Week 1 Status**: Basic retrieval and generation working. Citations and guardrails coming in Week 2.
""")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about Kubernetes..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Retrieving relevant documentation..."):
            # Retrieve chunks
            chunks = retrieve_chunks(prompt, top_k=5)
            
            if not chunks:
                response = "I couldn't find any relevant documentation for your question. Please try rephrasing."
            else:
                # Generate answer
                with st.spinner("Generating answer..."):
                    response = generate_answer(prompt, chunks)
        
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar with info
with st.sidebar:
    st.header("System Info")
    
    # Check if LanceDB is loaded
    try:
        table = load_lancedb_table()
        record_count = table.count_rows()
        st.success(f"✅ LanceDB connected")
        st.info(f"📊 {record_count:,} chunks indexed")
    except:
        st.error("❌ LanceDB not available")
    
    st.markdown("---")
    st.markdown("**Corpus**: Kubernetes Documentation")
    st.markdown("**Vector DB**: LanceDB")
    st.markdown("**Embeddings**: all-MiniLM-L6-v2")
    st.markdown(f"**LLM**: Ollama ({OLLAMA_MODEL})")
    
    # Check Ollama status
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        if response.status_code == 200:
            st.success("✅ Ollama connected")
        else:
            st.warning("⚠️ Ollama status unknown")
    except:
        st.error("❌ Ollama not running")
        st.caption("Run: `ollama serve`")
