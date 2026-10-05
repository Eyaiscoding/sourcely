"""
Load function: Stores chunks with embeddings in LanceDB.
"""

import os
from typing import List, Dict
import lancedb


def load(chunks: List[Dict], table_name: str = "kubernetes_docs") -> str:
    """
    Store chunks with embeddings in LanceDB.
    
    Args:
        chunks: List of dicts with {chunk_id, source_url, chunk_text, embedding}
        table_name: Name of the LanceDB table (default: 'kubernetes_docs')
    
    Returns:
        Path to the LanceDB database
    """
    lancedb_path = os.getenv("LANCEDB_PATH")
    
    if not lancedb_path:
        raise ValueError("LANCEDB_PATH environment variable not set")
    
    print(f"Connecting to LanceDB at: {lancedb_path}")
    
    # Connect to LanceDB (creates directory if it doesn't exist)
    db = lancedb.connect(lancedb_path)
    
    # Prepare data for LanceDB
    # LanceDB expects a list of dicts with consistent schema
    data = []
    for chunk in chunks:
        data.append({
            'chunk_id': chunk['chunk_id'],
            'source_url': chunk['source_url'],
            'chunk_text': chunk['chunk_text'],
            'embedding': chunk['embedding']
        })
    
    # Create or overwrite table
    try:
        # Check if table exists
        existing_tables = db.table_names()
        if table_name in existing_tables:
            print(f"Table '{table_name}' exists. Dropping and recreating...")
            db.drop_table(table_name)
        
        # Create table with data
        table = db.create_table(table_name, data)
        print(f"Created table '{table_name}' with {len(data)} records.")
    
    except Exception as e:
        print(f"Error creating table: {e}")
        # Try to append if creation failed
        try:
            table = db.open_table(table_name)
            table.add(data)
            print(f"Appended {len(data)} records to existing table '{table_name}'.")
        except Exception as append_error:
            raise Exception(f"Failed to create or append to table: {append_error}")
    
    print(f"Load complete. Stored {len(chunks)} chunks in LanceDB at {lancedb_path}")
    return lancedb_path
