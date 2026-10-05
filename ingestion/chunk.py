"""
Chunk function: Splits documents into manageable chunks.
"""

import re
from typing import List, Dict
import uuid


def chunk(docs: List[Dict[str, str]], target_tokens: int = 500) -> List[Dict[str, str]]:
    """
    Split documents into chunks of approximately target_tokens.
    
    Uses a simple heuristic: ~4 characters per token (English average).
    Splits on paragraph boundaries when possible, then sentence boundaries.
    
    Args:
        docs: List of dicts with {url, title, text}
        target_tokens: Target number of tokens per chunk (default: 500)
    
    Returns:
        List of dicts with {chunk_id, source_url, chunk_text}
    """
    chunks = []
    
    # Rough heuristic: ~4 characters per token
    target_chars = target_tokens * 4
    
    for doc in docs:
        url = doc['url']
        text = doc['text']
        
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If adding this paragraph would exceed target, save current chunk
            if current_chunk and len(current_chunk) + len(paragraph) > target_chars:
                chunk_id = str(uuid.uuid4())
                chunks.append({
                    'chunk_id': chunk_id,
                    'source_url': url,
                    'chunk_text': current_chunk.strip()
                })
                current_chunk = ""
            
            # If a single paragraph is too large, split by sentences
            if len(paragraph) > target_chars * 1.5:
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                for sentence in sentences:
                    if current_chunk and len(current_chunk) + len(sentence) > target_chars:
                        chunk_id = str(uuid.uuid4())
                        chunks.append({
                            'chunk_id': chunk_id,
                            'source_url': url,
                            'chunk_text': current_chunk.strip()
                        })
                        current_chunk = sentence + " "
                    else:
                        current_chunk += sentence + " "
            else:
                current_chunk += paragraph + "\n\n"
        
        # Add any remaining text as a chunk
        if current_chunk.strip():
            chunk_id = str(uuid.uuid4())
            chunks.append({
                'chunk_id': chunk_id,
                'source_url': url,
                'chunk_text': current_chunk.strip()
            })
    
    print(f"Chunking complete. Created {len(chunks)} chunks from {len(docs)} documents.")
    return chunks
