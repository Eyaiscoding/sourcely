# Sourcely Agent - Chat Interface

The Streamlit chat interface for querying Kubernetes documentation using RAG.

## Overview

This interface provides a conversational Q&A experience for Kubernetes documentation:
- **Retrieval**: Queries LanceDB for the top 5 most relevant chunks
- **Generation**: Uses Ollama (free local LLM) to generate answers
- **UI**: Streamlit chat interface with message history

## Week 1 Status

✅ **Implemented**:
- Embedding-based retrieval from LanceDB
- Context construction from retrieved chunks
- Answer generation with Claude
- Chat interface with history

❌ **Not Yet Implemented** (coming in Week 2):
- Source citations in answers
- Retrieval confidence scoring
- Safe answer fallbacks (refuse/hedge when confidence is low)
- Observability/tracing

## Prerequisites

1. **Ingestion pipeline must be completed**: The LanceDB database at `LANCEDB_PATH` must exist with indexed documentation
2. **Ollama must be installed and running**: 
   - Download from https://ollama.ai/download
   - Pull a model: `ollama pull llama3.2`
3. **Environment variables**: Ensure `.env` is configured with:
   - `OLLAMA_MODEL` - Model name (default: llama3.2)
   - `OLLAMA_BASE_URL` - Ollama API URL (default: http://localhost:11434)
   - `LANCEDB_PATH` - Path to LanceDB storage directory

## Running the Chat Interface

### Option 1: Direct Run

```powershell
streamlit run agent/app.py
```

The app will start on http://localhost:8501

### Option 2: From Project Root

```powershell
python -m streamlit run agent/app.py
```

## Usage

1. **Start the app**: Run one of the commands above
2. **Wait for initialization**: The app loads the embedding model and LanceDB table (cached after first load)
3. **Ask questions**: Type your question in the chat input at the bottom
4. **Review answers**: Claude will generate answers based on retrieved documentation

## Example Questions

- "What is a Kubernetes pod?"
- "How do I create a deployment?"
- "Explain Kubernetes services"
- "What are namespaces used for?"
- "How does kubectl work?"

## Architecture

```
User Question
    ↓
[Embed with all-MiniLM-L6-v2]
    ↓
[Search LanceDB for top 5 chunks]
    ↓
[Construct prompt with context]
    ↓
[Generate answer with Ollama (llama3.2)]
    ↓
Display Answer
```

## Troubleshooting

### "LanceDB not found"
- Run the ingestion pipeline first: `docker-compose -f ingestion/docker-compose.yml up` and trigger the DAG
- Verify `LANCEDB_PATH` in `.env` points to the correct directory

### "ANTHROPIC_API_KEY not configured"
- **Not needed anymore!** We switched to Ollama (free local LLM)
- Install Ollama: https://ollama.ai/download
- Pull a model: `ollama pull llama3.2`
- Restart the Streamlit app

### "Cannot connect to Ollama"
- Install Ollama from https://ollama.ai/download
- Verify it's running: `ollama list`
- Pull a model if you haven't: `ollama pull llama3.2`
- Check the service is running (Windows: runs automatically as a service)

### "Missing dependency"
- Install requirements: `pip install -r requirements.txt`

### Empty or incorrect answers
- Check that LanceDB contains data (sidebar shows record count)
- Try rephrasing your question
- Week 1 implementation is basic - improvements coming in Week 2

## Performance Notes

- **First run**: Loading the embedding model and LanceDB table takes ~10-30 seconds
- **Subsequent runs**: Models are cached, queries respond in ~5-15 seconds
- **Embedding latency**: ~100-200ms for query embedding
- **Retrieval latency**: ~50-100ms for LanceDB search
- **LLM latency**: ~2-10 seconds for Ollama generation (depends on model and hardware)
- **Local LLM**: Runs on your machine (CPU or GPU), no API costs, complete privacy

## Next Steps (Week 2+)

- Add source citations with paragraph-level references
- Implement retrieval confidence scoring
- Add safe answer fallbacks
- Integrate LangFuse for observability
- Track latency and cost per query
