# Sourcely Ingestion Pipeline - Airflow Orchestration

This directory contains the Airflow DAG and configuration for orchestrating the Kubernetes documentation ingestion pipeline.

## Overview

The ingestion pipeline consists of 3 sequential tasks:

1. **extract_and_upload**: Scrapes Kubernetes documentation and uploads raw HTML to Azure Blob Storage
2. **chunk_and_embed**: Chunks the documents and generates embeddings using sentence-transformers
3. **load_to_lancedb**: Stores the embedded chunks in LanceDB vector store

## Prerequisites

Before running the pipeline, ensure you have:

1. **Environment Variables**: Create a `.env` file in the project root with:
   ```env
   AZURE_STORAGE_CONNECTION_STRING=your_connection_string_here
   LANCEDB_PATH=./data/lancedb
   ```

2. **Docker and Docker Compose**: Required for running Airflow locally
   - Docker Desktop for Windows: https://www.docker.com/products/docker-desktop/

## Starting Airflow Locally

### Using Docker Compose (Recommended)

1. **Navigate to the ingestion directory**:
   ```powershell
   cd c:\Users\user\Desktop\PFA\sourcely\ingestion
   ```

2. **Start Airflow services**:
   ```powershell
   docker-compose up -d
   ```

   This will start:
   - PostgreSQL database (for Airflow metadata)
   - Airflow webserver (UI on port 8080)
   - Airflow scheduler (DAG execution)

3. **Wait for services to be healthy** (approximately 1-2 minutes):
   ```powershell
   docker-compose ps
   ```

4. **Access the Airflow UI**:
   - Open browser to http://localhost:8080
   - Default credentials:
     - Username: `admin`
     - Password: `admin`

### Stopping Airflow

```powershell
docker-compose down
```

To also remove volumes (database data):
```powershell
docker-compose down -v
```

## Running the DAG

### Manual Trigger via UI

1. **Access Airflow UI** at http://localhost:8080
2. **Log in** with admin/admin
3. **Locate the DAG**: Look for `kubernetes_docs_ingestion` in the DAG list
4. **Unpause the DAG**: Toggle the switch on the left to enable it
5. **Trigger manually**: Click the "Play" button (▶) on the right, then select "Trigger DAG"

### Manual Trigger via CLI

From inside the webserver container:

```powershell
docker-compose exec airflow-webserver airflow dags trigger kubernetes_docs_ingestion
```

### Scheduled Execution

The DAG is configured to run daily (`schedule_interval='@daily'`). Once unpaused, it will execute automatically according to this schedule.

## Monitoring Execution

### Via Web UI

1. **DAG View**: Click on the `kubernetes_docs_ingestion` DAG name
2. **Graph View**: Shows task dependencies and current status
   - Green = Success
   - Red = Failed
   - Yellow = Running
   - Light blue = Queued
3. **Task Logs**: Click on a task box, then "Log" to view detailed execution logs

### Via CLI

Check DAG status:
```powershell
docker-compose exec airflow-webserver airflow dags list
```

List DAG runs:
```powershell
docker-compose exec airflow-webserver airflow dags list-runs -d kubernetes_docs_ingestion
```

View task logs:
```powershell
docker-compose exec airflow-webserver airflow tasks logs kubernetes_docs_ingestion extract_and_upload <execution_date>
```

## Verifying Successful Execution

After the DAG completes successfully (all tasks green in UI):

1. **Check Azure Blob Storage**:
   - Verify the `raw-corpus` container contains uploaded HTML files
   - Use Azure Storage Explorer or Azure Portal

2. **Check LanceDB**:
   - Verify the LanceDB database exists at the path specified in `LANCEDB_PATH`
   - The `kubernetes_docs` table should contain embedded chunks

   ```powershell
   # Check LanceDB directory
   ls $env:LANCEDB_PATH
   ```

3. **Review Task Logs**:
   - Each task logs the count of processed items
   - Look for "complete" messages with counts

## Troubleshooting

### DAG not appearing in UI

- Check that DAG file has no syntax errors:
  ```powershell
  docker-compose exec airflow-webserver airflow dags list
  ```
- View scheduler logs:
  ```powershell
  docker-compose logs airflow-scheduler
  ```

### Tasks failing

1. **Check task logs** in the Airflow UI or via CLI
2. **Verify environment variables** are set correctly in `.env`
3. **Ensure dependencies are installed** (check `_PIP_ADDITIONAL_REQUIREMENTS` in docker-compose.yml)
4. **Check for Azure connectivity** if upload_raw fails
5. **Verify LanceDB path is writable** if load fails

### ImportError for ingestion modules

- Ensure the ingestion directory is mounted correctly in docker-compose.yml
- Check that `sys.path.insert` in the DAG file points to the correct path

### Out of memory errors

- Reduce `max_pages` in the `extract()` call (default 150)
- Consider using a smaller embedding model
- Allocate more memory to Docker Desktop (Settings → Resources)

## DAG Configuration

The DAG can be customized by editing `/ingestion/dags/kubernetes_docs_ingestion.py`:

- **Schedule**: Change `schedule_interval` parameter (e.g., `'@weekly'`, `'@hourly'`, or cron expression)
- **Max pages**: Modify `max_pages` in `extract()` call
- **Chunk size**: Adjust `target_tokens` in `chunk()` call
- **Embedding model**: Change `model_name` in `embed()` call
- **Retry behavior**: Modify `default_args` (retries, retry_delay)

## Architecture Notes

- **Postgres backend**: Used for storing Airflow metadata and DAG run history
- **LocalExecutor**: Tasks run sequentially on the scheduler machine
- **XCom**: Used to pass data between tasks (documents, chunks)
- **Volume mounts**: DAG code and logs are persisted on the host

## Next Steps

After successful DAG execution:

1. Verify data quality in LanceDB
2. Test the chat interface (`/agent/app.py`) to query the indexed documentation
3. Monitor DAG performance and adjust chunk size / max pages as needed
4. Consider adding data quality checks as additional tasks
5. Set up alerting for DAG failures (email notifications in `default_args`)
