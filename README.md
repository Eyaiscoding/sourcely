# Sourcely

Production-grade RAG system for Kubernetes documentation Q&A using LanceDB, Ollama, and Airflow orchestration.

## Overview

Sourcely is a 4-week academic project demonstrating MLOps best practices: automated ingestion pipelines, vector search, local LLM inference, and infrastructure as code. The system answers technical questions grounded in Kubernetes docs with full observability and quality tracking.

**Current Status**: Week 1 Complete ✅

## Features

- 🔍 **Semantic Search**: LanceDB vector database with sentence-transformers embeddings
- 🤖 **Free LLM**: Local inference with Ollama (llama3.2) - zero API costs
- ⚙️ **Orchestration**: Airflow DAG for automated ingestion pipeline
- ☁️ **Cloud Storage**: Azure Blob Storage for raw corpus with Terraform IaC
- 💬 **Chat Interface**: Streamlit UI with conversation history
- 📊 **MLOps Ready**: Structured for eval suite, tracking, and deployment (Week 2+)

## Quick Start

### Prerequisites

- Python 3.11 or 3.12
- Docker (for Airflow)
- Terraform
- Azure subscription (free tier sufficient)
- [Ollama](https://ollama.ai) with llama3.2 model

### Installation

1. **Clone and configure**:
   ```bash
   git clone https://github.com/<your-username>/sourcely.git
   cd sourcely
   cp .env.example .env
   # Edit .env with your Azure credentials
   ```

2. **Install Ollama and pull model**:
   ```bash
   # Download from https://ollama.ai/download
   ollama pull llama3.2
   ```

3. **Provision infrastructure**:
   ```bash
   cd infra
   # Follow bootstrap instructions in infra/README.md
   terraform init && terraform apply
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run ingestion pipeline**:
   ```bash
   cd ingestion
   docker-compose up -d
   # Trigger 'kubernetes_docs_ingestion' DAG at http://localhost:8080
   ```

6. **Start chat interface**:
   ```bash
   streamlit run agent/app.py
   # Access at http://localhost:8501
   ```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Ingestion Pipeline                      │
│  (Airflow DAG: extract → chunk → embed → load)             │
│                                                             │
│  Kubernetes Docs → Azure Blob → LanceDB Vector Store       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Query Pipeline                         │
│  Question → Embed → Retrieve → Generate (Ollama) → Answer  │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Ollama (llama3.2) |
| Embeddings | sentence-transformers |
| Vector DB | LanceDB |
| Orchestration | Apache Airflow |
| Storage | Azure Blob Storage |
| Infrastructure | Terraform |
| UI | Streamlit |

## Project Structure

```
sourcely/
├── ingestion/          # ETL pipeline (extract, chunk, embed, load)
│   └── dags/          # Airflow DAG definitions
├── agent/             # Streamlit chat interface
├── infra/             # Terraform configurations
├── eval/              # Evaluation suite (Week 2+)
└── requirements.txt   # Python dependencies
```

## Roadmap

- [x] **Week 1**: End-to-end RAG pipeline with Airflow orchestration
- [ ] **Week 2**: Citations, eval suite, LangFuse observability, MLflow tracking
- [ ] **Week 3**: Retrieval confidence scoring, DVC versioning, dbt analytics
- [ ] **Week 4**: Azure deployment, final report with iteration analysis

## Documentation

- [Infrastructure Setup](infra/README.md) - Terraform and Azure configuration
- [Ingestion Pipeline](ingestion/README.md) - Airflow DAG and data processing
- [Chat Agent](agent/README.md) - Streamlit interface usage

## Development

**Commit Conventions**: Small, focused commits with clear messages  
**Branch Strategy**: Direct to main for solo work, feature branches for collaboration  
**Testing**: Manual verification (Week 1), automated tests (Week 2+)

## License

Academic project - not licensed for external use.

---

**Status**: Week 1 Complete | **Next**: Citations & Observability
