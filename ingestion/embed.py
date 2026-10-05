"""
Embed function: Generates embeddings for text chunks.
"""

from typing import List, Dict
from sentence_transformers import SentenceTransformer


def embed(chunks: List[Dict[str, str]], model_name: str = "all-MiniLM-L6-v2") -> List[Dict]:
    """
    Generate embeddings for text chunks using sentence-transformers.
    
    Args:
        chunks: List of dicts with {chunk_id, source_url, chunk_text}
        model_name: Name of the sentence-transformers model (default: 'all-MiniLM-L6-v2')
    
    Returns:
        List of chunks enriched with 'embedding' field (list of floats)
    """
    print(f"Loading model: {model_name}")
    model = SentenceTransformer(model_name)
    
    # Extract texts for batch encoding
    texts = [chunk['chunk_text'] for chunk in chunks]
    
    print(f"Generating embeddings for {len(texts)} chunks...")
    
    # Generate embeddings in batch for efficiency
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    
    # Add embeddings to chunks
    enriched_chunks = []
    for i, chunk in enumerate(chunks):
        enriched_chunk = chunk.copy()
        enriched_chunk['embedding'] = embeddings[i].tolist()
        enriched_chunks.append(enriched_chunk)
    
    print(f"Embedding complete. Generated {len(enriched_chunks)} embeddings.")
    return enriched_chunks
