<div align="center">
  
# TroyAI - Video Compliance QA Pipeline
**v1.0.0**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge&logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991.svg?style=for-the-badge&logo=OpenAI&logoColor=white)](https://openai.com/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C.svg?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com/)

An automated, robust, and production-ready Video Compliance QA Pipeline orchestrated by **LangGraph**, designed to audit multimodal content against strict regulatory standards using a Retrieval-Augmented Generation (RAG) architecture.

</div>

---

## Overview

TroyAI establishes an end-to-end system that transforms unstructured video content into structured, actionable JSON compliance reports with deep full-stack observability. 

1. **Ingestion & Processing:** Leverages **yt-dlp** and **Azure Video Indexer** for multimodal ingestion, extracting deep insights such as video transcripts and On-Screen Text (OCR).
2. **Retrieval-Augmented Generation (RAG):** Uses **Azure AI Search** and **Azure OpenAI Embeddings** to semantically retrieve relevant compliance and regulatory rules from the knowledge base.
3. **Reasoning Engine:** Orchestrates the flow using **LangGraph** and utilizes **Azure OpenAI (GPT-4o)** to synthesize the extracted insights against retrieved rules to deterministically detect violations.
4. **Observability:** Granular LLM tracing is provided natively via **LangSmith**, while system-level production telemetry is routed to **Azure Application Insights** via OpenTelemetry.

---

## Features

- **Multi-Modal Audit:** Audits both spoken transcript and visual on-screen text (OCR) concurrently.
- **Agentic Workflow:** Built on LangGraph state graphs (`indexer` → `auditor`) for fault-tolerant and deterministic pipeline orchestration.
- **Production-Ready API:** Exposed as a blazing-fast, robust RESTful API using FastAPI.
- **Deep Observability:** Built-in hooks for both AI telemetry (LangSmith) and Application telemetry (Azure Monitor).
- **Extensible Compliance:** Easily update regulatory rules through the Azure AI Search knowledge base vector index.

---

##  Getting Started

### Prerequisites
- Python 3.10+
- `uv` package manager installed
- Active Azure Subscription (Video Indexer, AI Search, OpenAI, Application Insights)
- Active LangSmith Account (for LLM observability)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/ComplianceQAPipeline.git
   cd ComplianceQAPipeline
   ```

2. **Install Dependencies and Setup Environment**
   This project uses `uv` for lightning-fast package management and lockfiles (`uv.lock` and `pyproject.toml`). You do **not** need a `requirements.txt` file. You can automatically create the virtual environment and install all locked dependencies perfectly using a single command:
   ```bash
   uv sync
   ```

3. **Activate the Virtual Environment**
   ```bash
   # On macOS/Linux:
   source .venv/bin/activate
   # On Windows:
   # .venv\Scripts\activate
   ```

---

## Environment Configuration

Create a `.env` file in the root of the `ComplianceQAPipeline` directory with the following configuration:

```env
# Azure Storage
AZURE_STORAGE_CONNECTION_STRING="your_storage_connection_string"

# Azure OpenAI (Reasoning & Embeddings)
AZURE_OPENAI_ENDPOINT="https://your-openai-endpoint.cognitiveservices.azure.com/"
AZURE_OPENAI_API_KEY="your_openai_api_key"
AZURE_OPENAI_API_VERSION="2024-12-01-preview"
AZURE_OPENAI_CHAT_DEPLOYMENT="gpt-4o"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-3-small-sunrise"

# Azure AI Search (RAG Knowledgebase)
AZURE_SEARCH_ENDPOINT="https://your-search-endpoint.search.windows.net"
AZURE_SEARCH_API_KEY="your_search_api_key"
AZURE_SEARCH_INDEX_NAME="compliance-rules"

# Azure Video Indexer
AZURE_VI_NAME="your-vid-indexer-name"
AZURE_VI_LOCATION="eastus2"
AZURE_VI_ACCOUNT_ID="your_account_id"
AZURE_SUBSCRIPTION_ID="your_subscription_id"
AZURE_RESOURCE_GROUP="your_resource_group"

# Azure Application Insights (Telemetry)
APPLICATIONINSIGHTS_CONNECTION_STRING="your_app_insights_connection_string"

# LangSmith (LLM Observability)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="your_langchain_api_key"
LANGCHAIN_PROJECT_NAME="troy"
```

*Note: Ensure you are logged into the Azure CLI (`az login`) or provide standard Azure Service Principal credentials for `DefaultAzureCredential` to authenticate with Video Indexer successfully.*

---

## 🏃 Running the API Server

Start the FastAPI application using `uvicorn`:

```bash
uvicorn backend.src.api.server:app --reload --host 0.0.0.0 --port 8000
```

The API will now be running at `http://localhost:8000`.
You can access the interactive Swagger documentation at `http://localhost:8000/docs`.

---

##  API Endpoints

### 1. System Health
**`GET /health`**
Verifies the operational status of the TroyAI service.
```bash
curl -X GET http://localhost:8000/health
```
**Response:**
```json
{
  "status": "health",
  "service": "TroyAI"
}
```

### 2. Audit Video
**`POST /audit`**
Triggers the LangGraph automated compliance audit pipeline for a given YouTube URL.

```bash
curl -X POST http://localhost:8000/audit \
     -H "Content-Type: application/json" \
     -d '{"video_url": "https://youtu.be/exampleID"}'
```

**Response:**
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "video_id": "vid_a1b2c3d4",
  "status": "FAIL",
  "final_report": "The video fails to comply with multiple regulatory rules. It makes unsubstantiated claims about the product's performance...",
  "compliance_results": [
    {
      "category": "Claim Validation",
      "severity": "CRITICAL",
      "description": "The claim 'Ultra Sheer gives you high SPF protection' is made without scientific proof..."
    }
  ]
}
```

---

## Telemetry and Observability

TroyAI is built with "Day 2" operations in mind:
- **Application Logic:** Native python `logging` is bound with Azure Monitor OpenTelemetry (`azure.monitor.opentelemetry`). Application insights capture metrics, exceptions, and API latency.
- **LLM Tracing:** LangChain traces (Prompts, Token Usage, Chain-of-Thought) are streamed real-time to your LangSmith Dashboard project (`troy`).