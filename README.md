# Sourcely - Kubernetes Documentation Q&A Agent

A production-grade documentation Q&A agent built with RAG (Retrieval-Augmented Generation). This system answers technical questions grounded in Kubernetes documentation, with complete MLOps tracking from day one.

## 🎯 Project Overview

**Sourcely** is a 4-week academic project building a support-style chat agent that:
- Answers questions using Kubernetes documentation as the corpus
- Cites source paragraphs for every answer
- Falls back to "safe answers" when retrieval confidence is low
- Tracks quality via an eval suite that gates every deploy
- Provides full observability (traces, latency, cost per query)

### Week 1 Status: ✅ End-to-End Pipeline Working

**What's implemented:**
- ✅ Repository scaffolding and Git initialization
- ✅ Environment configuration (`.env` setup)
- ✅ Azure Blob Storage via Terraform (infrastructure as code)
- ✅ Ingestion pipeline (extract → upload → chunk → embed → load)
- ✅ Airflow DAG orchestration
- ✅ LanceDB vector database with embeddings
- ✅ Streamlit chat interface with Claude 3.5 Sonnet
- ✅ Raw corpus stored in Azure Blob Storage

**Not yet implemented (Week 2+):**
- Citations in answers
- Retrieval confidence scoring and safe answer fallbacks
- LangFuse observability/tracing
- Eval suite
- MLflow tracking
- DVC versioning
- dbt analytics models

## 🏗️ Architecture

### Tech Stack

| Component | Technology |
|-----------|-----------|
| **LLM** | Anthropic Claude 3.5 Sonnet |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |
| **Vector DB** | LanceDB (embedded) |
| **Orchestration** | Apache Airflow |
| **Cloud Storage** | Azure Blob Storage |
| **Infrastructure** | Terraform |
| **Chat UI** | Streamlit |
| **Corpus** | Kubernetes Documentation (~150 pages) |

### Pipeline Flow

```
Ingestion Pipeline (Airflow DAG):
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Extract   │ -> │ Chunk/Embed  │ -> │ Load to DB  │
│   K8s Docs  │    │              │    │  (LanceDB)  │
└─────────────┘    └──────────────┘    └─────────────┘
      │
      ↓
┌─────────────┐
│ Upload Raw  │
│ to Azure    │
│ Blob Store  │
└─────────────┘

Query Pipeline (Streamlit App):
User Question -> Embed -> Search LanceDB -> Retrieve Top-K -> Generate with Claude -> Answer
```

## 📋 Prerequisites

### Required Software

- **Python**: 3.11 or 3.12 (3.13 has PyTorch compatibility issues)
- **Terraform**: For infrastructure provisioning
- **Docker**: For running Airflow locally
- **Azure CLI**: For Azure authentication
- **Git**: Version control

### Required Accounts & Keys

- **Azure Subscription**: For Blob Storage (free tier works)
- **Anthropic API Key**: For Claude access
- **GitHub Account**: For public repository hosting

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/sourcely.git
cd sourcely
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your values:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and add your credentials:

```env
# LLM Configuration
ANTHROPIC_API_KEY=sk-ant-...

# Vector Database
LANCEDB_PATH=./data/lancedb

# Azure Storage (after Terraform apply)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
AZURE_STORAGE_CONTAINER_NAME=raw-corpus

# Azure ML (Week 2+)
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=sourcely-rg
AZURE_ML_WORKSPACE_NAME=sourcely-ml-workspace
MLFLOW_TRACKING_URI=

# LangFuse (Week 2+)
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=
```

### 3. Provision Azure Infrastructure

Navigate to the infrastructure directory and follow the Terraform setup:

```powershell
cd infra
```

**Important**: Read `infra/README.md` first for the manual bootstrap step (creating the Terraform state storage).

After bootstrap:

```powershell
terraform init
terraform plan
terraform apply
```

This creates:
- Azure Resource Group
- Azure Storage Account
- Blob Container (`raw-corpus`)

Copy the connection string from the output and add it to your `.env` file.

**Detailed instructions**: See [infra/README.md](infra/README.md)

### 4. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

**Note**: If you encounter PyTorch errors with Python 3.13, use Python 3.11 or 3.12, or install PyTorch separately:

```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### 5. Run the Ingestion Pipeline

The ingestion pipeline is orchestrated by Airflow. Start Airflow:

```powershell
cd ingestion
docker-compose up -d
```

Access the Airflow UI at http://localhost:8080 (default credentials: airflow/airflow)

**Trigger the DAG:**
1. Navigate to http://localhost:8080
2. Find the `kubernetes_docs_ingestion` DAG
3. Click "Trigger DAG" button
4. Monitor the 3 tasks: `extract_and_upload` → `chunk_and_embed` → `load_to_lancedb`

This will:
- Scrape ~150 pages from Kubernetes docs
- Upload raw HTML to Azure Blob Storage
- Chunk the content into ~500-token segments
- Generate embeddings using sentence-transformers
- Load everything into LanceDB

**Expected duration**: 10-30 minutes (depending on network speed)

**Detailed instructions**: See [ingestion/README.md](ingestion/README.md)

### 6. Run the Chat Interface

Once the ingestion is complete, start the Streamlit app:

```powershell
streamlit run agent/app.py
```

Access the chat interface at http://localhost:8501

**Try asking:**
- "What is a Kubernetes pod?"
- "How do I create a deployment?"
- "Explain Kubernetes services"

**Detailed instructions**: See [agent/README.md](agent/README.md)

## 📁 Project Structure

```
sourcely/
├── .env                          # Environment variables (gitignored)
├── .env.example                  # Environment template (committed)
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── README.md                     # This file
│
├── ingestion/                    # Ingestion pipeline
│   ├── dags/                     # Airflow DAG definitions
│   │   ├── __init__.py
│   │   └── kubernetes_docs_ingestion.py
│   ├── __init__.py
│   ├── config.py                 # Environment variable loader
│   ├── extract.py                # Scrape Kubernetes docs
│   ├── upload_raw.py             # Upload to Azure Blob Storage
│   ├── chunk.py                  # Text chunking
│   ├── embed.py                  # Generate embeddings
│   ├── load.py                   # Load to LanceDB
│   ├── docker-compose.yml        # Airflow local setup
│   └── README.md                 # Ingestion docs
│
├── agent/                        # Chat interface
│   ├── __init__.py
│   ├── app.py                    # Streamlit app
│   └── README.md                 # Agent docs
│
├── infra/                        # Infrastructure as code
│   ├── main.tf                   # Azure resources
│   ├── variables.tf              # Terraform variables
│   ├── backend.tf                # Remote state config
│   ├── terraform.tfvars.example  # Variable template
│   └── README.md                 # Infrastructure docs
│
└── eval/                         # Evaluation suite (Week 2+)
    └── (empty - coming soon)
```

## 🔄 Development Workflow

### Making Changes

1. **Create a feature branch** (optional for solo work):
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make your changes** and test locally

3. **Commit frequently** with clear messages:
   ```bash
   git add .
   git commit -m "feat: add retrieval confidence scoring"
   ```

4. **Push to GitHub**:
   ```bash
   git push origin main
   # or: git push origin feature/your-feature
   ```

### Running Tests

Week 1 has minimal testing (just manual verification). Automated tests coming in Week 2+.

### Checking Logs

**Airflow logs**: http://localhost:8080 → DAGs → kubernetes_docs_ingestion → Task → Logs

**Streamlit logs**: Check the terminal where `streamlit run` is running

## 🎓 Week-by-Week Roadmap

- **Week 1** (Current): ✅ End-to-end pipeline, rough but working
- **Week 2**: Add citations, observability (LangFuse), eval suite, MLflow tracking
- **Week 3**: Safe answer fallbacks, DVC versioning, dbt analytics, iteration on quality
- **Week 4**: Deploy to Azure Container Apps, final report with before/after comparison

## 🐛 Troubleshooting

### "LanceDB not found"
- Ensure the ingestion pipeline has run successfully
- Check that `LANCEDB_PATH` in `.env` points to the correct directory
- Verify the Airflow DAG completed all 3 tasks

### "ANTHROPIC_API_KEY not configured"
- Add your API key to `.env`
- Restart the Streamlit app

### "Azure Storage connection failed"
- Verify `AZURE_STORAGE_CONNECTION_STRING` in `.env`
- Check that Terraform apply succeeded
- Test connection: `az storage container list --connection-string "..."`

### PyTorch import errors (Python 3.13)
- Use Python 3.11 or 3.12
- Or install PyTorch separately: `pip install torch --index-url https://download.pytorch.org/whl/cpu`

### Airflow DAG not appearing
- Check Docker containers are running: `docker ps`
- Verify DAG file has no syntax errors: `python ingestion/dags/kubernetes_docs_ingestion.py`
- Check Airflow logs: `docker-compose -f ingestion/docker-compose.yml logs`

## 📚 Additional Documentation

- **Infrastructure setup**: [infra/README.md](infra/README.md)
- **Ingestion pipeline**: [ingestion/README.md](ingestion/README.md)
- **Chat interface**: [agent/README.md](agent/README.md)

## 🤝 Contributing

This is an academic project for a 2-person team. If you're the other teammate:

1. Clone the repo
2. Create your own `.env` with your Azure credentials
3. Create a feature branch for your work
4. Commit and push frequently
5. Keep commits small and focused

## 📝 License

Academic project - not licensed for external use.

## 📧 Contact

For questions or issues, contact the project team or refer to the course materials.

---

**Status**: Week 1 Complete ✅ | Next Up: Week 2 - Citations & Observability
