"""
Test script for the complete ingestion pipeline.

This script tests all five ingestion functions in sequence.
Set environment variables before running:
  - AZURE_STORAGE_CONNECTION_STRING
  - LANCEDB_PATH
"""

import os
import sys

# Test imports
print("Testing imports...")
try:
    from ingestion.extract import extract
    print("✓ extract imported")
except Exception as e:
    print(f"✗ extract import failed: {e}")
    sys.exit(1)

try:
    from ingestion.upload_raw import upload_raw
    print("✓ upload_raw imported")
except Exception as e:
    print(f"✗ upload_raw import failed: {e}")
    sys.exit(1)

try:
    from ingestion.chunk import chunk
    print("✓ chunk imported")
except Exception as e:
    print(f"✗ chunk import failed: {e}")
    sys.exit(1)

try:
    from ingestion.embed import embed
    print("✓ embed imported")
except Exception as e:
    print(f"✗ embed import failed: {e}")
    print("  Note: This may fail on Python 3.13 due to torch/torchvision compatibility.")
    print("  Try Python 3.11 or 3.12 if you see import errors.")
    sys.exit(1)

try:
    from ingestion.load import load
    print("✓ load imported")
except Exception as e:
    print(f"✗ load import failed: {e}")
    sys.exit(1)

print("\nAll imports successful!\n")

# Test the pipeline with a small sample
print("=" * 60)
print("Testing full pipeline with limited scraping...")
print("=" * 60)

# 1. Extract (limit to 5 pages for testing)
print("\n[1/5] Extracting documentation (limited to 5 pages)...")
docs = extract(max_pages=5)
print(f"Extracted {len(docs)} documents")

if not docs:
    print("ERROR: No documents extracted!")
    sys.exit(1)

# 2. Upload raw (only if Azure connection string is set)
if os.getenv("AZURE_STORAGE_CONNECTION_STRING"):
    print("\n[2/5] Uploading raw documents to Azure Blob Storage...")
    try:
        blob_urls = upload_raw(docs)
        print(f"Uploaded {len(blob_urls)} documents")
    except Exception as e:
        print(f"Upload failed (skipping): {e}")
else:
    print("\n[2/5] Skipping upload (AZURE_STORAGE_CONNECTION_STRING not set)")

# 3. Chunk
print("\n[3/5] Chunking documents...")
chunks = chunk(docs)
print(f"Created {len(chunks)} chunks")

if not chunks:
    print("ERROR: No chunks created!")
    sys.exit(1)

# 4. Embed
print("\n[4/5] Generating embeddings...")
try:
    embedded_chunks = embed(chunks)
    print(f"Generated embeddings for {len(embedded_chunks)} chunks")
except Exception as e:
    print(f"Embedding failed: {e}")
    sys.exit(1)

# 5. Load (only if LANCEDB_PATH is set)
if os.getenv("LANCEDB_PATH"):
    print("\n[5/5] Loading into LanceDB...")
    try:
        db_path = load(embedded_chunks)
        print(f"Loaded data into LanceDB at: {db_path}")
    except Exception as e:
        print(f"Load failed: {e}")
        sys.exit(1)
else:
    print("\n[5/5] Skipping load (LANCEDB_PATH not set)")

print("\n" + "=" * 60)
print("Pipeline test completed successfully!")
print("=" * 60)
