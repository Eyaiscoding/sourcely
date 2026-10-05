"""
Airflow DAG for Kubernetes documentation ingestion pipeline.

This DAG orchestrates the complete ingestion pipeline:
1. Extract and upload: Scrapes Kubernetes docs and uploads to Azure Blob Storage
2. Chunk and embed: Chunks documents and generates embeddings
3. Load to LanceDB: Stores embedded chunks in LanceDB vector store
"""

import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Add parent directory to path to import ingestion modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extract import extract
from upload_raw import upload_raw
from chunk import chunk
from embed import embed
from load import load


# Default arguments for the DAG
default_args = {
    'owner': 'sourcely',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def extract_and_upload_task(**context):
    """
    Task 1: Extract Kubernetes docs and upload raw HTML to Azure Blob Storage.
    """
    print("Starting extraction...")
    docs = extract(start_url="https://kubernetes.io/docs/", max_pages=150)
    
    print("Starting upload...")
    blob_urls = upload_raw(docs, container_name="raw-corpus")
    
    # Push docs to XCom for next task
    context['task_instance'].xcom_push(key='docs', value=docs)
    
    return {
        'docs_count': len(docs),
        'blob_urls_count': len(blob_urls)
    }


def chunk_and_embed_task(**context):
    """
    Task 2: Chunk documents and generate embeddings.
    """
    # Pull docs from previous task
    docs = context['task_instance'].xcom_pull(task_ids='extract_and_upload', key='docs')
    
    if not docs:
        raise ValueError("No documents received from extract_and_upload task")
    
    print(f"Starting chunking for {len(docs)} documents...")
    chunks = chunk(docs, target_tokens=500)
    
    print(f"Starting embedding for {len(chunks)} chunks...")
    embedded_chunks = embed(chunks, model_name="all-MiniLM-L6-v2")
    
    # Push embedded chunks to XCom for next task
    context['task_instance'].xcom_push(key='embedded_chunks', value=embedded_chunks)
    
    return {
        'chunks_count': len(embedded_chunks)
    }


def load_to_lancedb_task(**context):
    """
    Task 3: Load embedded chunks into LanceDB.
    """
    # Pull embedded chunks from previous task
    embedded_chunks = context['task_instance'].xcom_pull(task_ids='chunk_and_embed', key='embedded_chunks')
    
    if not embedded_chunks:
        raise ValueError("No embedded chunks received from chunk_and_embed task")
    
    print(f"Starting load for {len(embedded_chunks)} embedded chunks...")
    lancedb_path = load(embedded_chunks, table_name="kubernetes_docs")
    
    return {
        'lancedb_path': lancedb_path,
        'loaded_count': len(embedded_chunks)
    }


# Define the DAG
with DAG(
    'kubernetes_docs_ingestion',
    default_args=default_args,
    description='Extract, chunk, embed, and load Kubernetes documentation into LanceDB',
    schedule_interval='@daily',  # Runs daily, can also be triggered manually
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['ingestion', 'kubernetes', 'docs'],
) as dag:
    
    # Task 1: Extract and upload
    task_extract_and_upload = PythonOperator(
        task_id='extract_and_upload',
        python_callable=extract_and_upload_task,
        provide_context=True,
    )
    
    # Task 2: Chunk and embed
    task_chunk_and_embed = PythonOperator(
        task_id='chunk_and_embed',
        python_callable=chunk_and_embed_task,
        provide_context=True,
    )
    
    # Task 3: Load to LanceDB
    task_load_to_lancedb = PythonOperator(
        task_id='load_to_lancedb',
        python_callable=load_to_lancedb_task,
        provide_context=True,
    )
    
    # Define task dependencies (chain tasks sequentially)
    task_extract_and_upload >> task_chunk_and_embed >> task_load_to_lancedb
