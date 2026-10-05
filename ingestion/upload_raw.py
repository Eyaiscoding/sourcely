"""
Upload raw function: Uploads raw documentation to Azure Blob Storage.
"""

import os
import hashlib
from typing import List, Dict
from azure.storage.blob import BlobServiceClient


def upload_raw(docs: List[Dict[str, str]], container_name: str = "raw-corpus") -> List[str]:
    """
    Upload raw documentation to Azure Blob Storage.
    
    Args:
        docs: List of dicts with {url, title, raw_html, text}
        container_name: Name of the Azure Blob Storage container (default: 'raw-corpus')
    
    Returns:
        List of blob URLs for uploaded documents
    """
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    
    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING environment variable not set")
    
    # Initialize blob service client
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    # Create container if it doesn't exist
    try:
        container_client = blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()
            print(f"Created container: {container_name}")
    except Exception as e:
        print(f"Container operation note: {e}")
    
    blob_urls = []
    
    for doc in docs:
        try:
            # Create a safe blob name from URL hash
            url_hash = hashlib.md5(doc['url'].encode()).hexdigest()
            blob_name = f"{url_hash}.html"
            
            # Upload the raw HTML
            blob_client = blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            blob_client.upload_blob(
                doc['raw_html'],
                overwrite=True,
                metadata={
                    'source_url': doc['url'],
                    'title': doc['title']
                }
            )
            
            blob_url = blob_client.url
            blob_urls.append(blob_url)
            
            print(f"Uploaded: {doc['title']} -> {blob_name}")
        
        except Exception as e:
            print(f"Error uploading {doc['url']}: {e}")
            continue
    
    print(f"Upload complete. Uploaded {len(blob_urls)} documents.")
    return blob_urls
