"""
Configuration module for Sourcely.
Loads environment variables from .env file using python-dotenv.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
project_root = Path(__file__).parent.parent
dotenv_path = project_root / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Anthropic API key for Claude (DEPRECATED - using Ollama instead)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Ollama configuration (free local LLM)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# LanceDB path for vector storage
LANCEDB_PATH = os.getenv("LANCEDB_PATH", "./lancedb_data")

# Azure Storage connection string
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")

# Azure Storage container name
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "sourcely-raw-corpus")

# Azure subscription ID
AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID", "")

# Azure resource group
AZURE_RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP", "")

# Azure ML workspace name
AZURE_ML_WORKSPACE_NAME = os.getenv("AZURE_ML_WORKSPACE_NAME", "")

# MLflow tracking URI
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "")

# Langfuse public key
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")

# Langfuse secret key
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")

# Langfuse host
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
