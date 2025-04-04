# HerpAI-Ingestion

A flexible and scalable library for ingesting, processing, and storing biomedical data from various sources, built for the HerpAI Project to enrich AI Agents with domain-specific knowledge and power Retrieval-Augmented Generation (RAG) systems.

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 💬 Join the Community

Come chat with us on Discord: [HerpAI Discord Server](https://discord.gg/72dWs7J9)

## Overview

HerpAI-Ingestion is a powerful toolkit designed for the extraction, transformation, and loading (ETL) of biomedical data from multiple public repositories. Built on top of the HerpAI-CoreLib, it implements a unified interface for accessing diverse data sources while maintaining a clean separation between business logic and deployment infrastructure.

### Purpose and Integration with HerpAI Project

This library serves as a critical component in the HerpAI ecosystem, with the primary purpose of:

1. **Knowledge Acquisition**: Systematically gathering domain-specific knowledge about herpes viruses and related treatments from authoritative sources
2. **Data Enrichment**: Processing and structuring this data for consumption by AI systems
3. **RAG Enablement**: Providing the knowledge foundation for Retrieval-Augmented Generation (RAG) systems that power HerpAI Agents
4. **Domain Specialization**: Ensuring HerpAI's AI capabilities are grounded in accurate, up-to-date biomedical information

The ingested data flows directly into HerpAI's knowledge stores, allowing AI agents to retrieve and reference specific scientific information when answering queries, making recommendations, or analyzing research trends.

## Features

- **Multiple Source Connectors**: Unified interface for PubMed, Europe PMC, ClinicalTrials.gov, and more
- **Document Processing**: PDF parsing and structured extraction using GROBID
- **Data Lake Storage**: Support for S3, NFS, and Azure Blob Storage backends
- **Metadata Cataloging**: Database storage for structured metadata and querying
- **Deployment Flexibility**: Run locally, in containers, or in Kubernetes
- **Distributed Processing**: Optional RabbitMQ integration for scalable processing
- **Scheduled Ingestion**: Cron-based scheduling for automated data updates
- **Retry Mechanisms**: Comprehensive error handling with exponential backoff

## Architecture

HerpAI-Ingestion follows a modular, decoupled architecture with these key components:

1. **Connector SDK**: A lightweight SDK that defines interfaces and base classes for data source connectors
2. **Core Ingestion System**: The main application that orchestrates data ingestion and processing
3. **Connector Plugins**: Individual implementations for different data sources (PubMed, ClinicalTrials, etc.)
4. **Message Queue**: Optional RabbitMQ integration for distributed processing

### Connector Architecture

The system uses a plugin-based connector architecture:

- **Connector SDK**: Defines the `IConnector` interface and common functionality
- **Connector Specifications**: Each connector includes a YAML specification file that defines its capabilities and configuration
- **Connector Registry**: Discovers and loads available connectors at runtime
- **Decoupled Implementation**: Connectors depend only on the SDK, not on the ingestion system

```
┌─────────────────────────────────────────────────────────────┐
│                      HerpAI Ingestion                       │
│                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌────────────────────┐ │
│  │   Ingestion │   │   Document  │   │      Connector     │ │
│  │   Service   │◄──┤  Repository │◄──┤      Registry      │ │
│  └─────────────┘   └─────────────┘   └────────────────────┘ │
│         │                                      ▲            │
└─────────┼──────────────────────────────────────┼────────────┘
          │                                      │
          ▼                                      │
┌─────────────────┐                   ┌─────────────────────┐
│     RabbitMQ    │                   │   Connector SDK     │
└─────────────────┘                   └─────────────────────┘
          ▲                                      ▲
          │                                      │
┌─────────┼──────────────────────────────────────┼────────────┐
│         │           Connector Plugins          │            │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐   │
│  │    PubMed   │   │ ClinicalT.  │   │   Europe PMC    │   │
│  │  Connector  │   │  Connector  │   │    Connector    │   │
│  └─────────────┘   └─────────────┘   └─────────────────┘   │
│  connector.yaml    connector.yaml    connector.yaml        │
└─────────────────────────────────────────────────────────────┘
```

This architecture ensures that:
- Connectors can be developed independently
- The ingestion system can evolve without breaking connectors
- New data sources can be added without modifying the core system

## Project Structure

The project is organized as a monorepo with clear separation between components:

```
herpai-ingestion/
├── README.md
├── pyproject.toml
├── LICENSE
│
├── herpai_connector_sdk/        # The connector SDK (future separate package)
│   ├── __init__.py
│   ├── interfaces.py            # Core interfaces (IConnector)
│   ├── base.py                  # Base implementations (BaseConnector)
│   ├── models.py                # Data models (Document)
│   ├── exceptions.py            # Custom exceptions
│   └── utils/                   # Utilities for connectors
│
├── herpai_ingestion/            # Main ingestion system
│   ├── __init__.py
│   ├── cli/                     # Command-line interface
│   ├── services/                # Business logic services
│   ├── workers/                 # Background workers
│   └── utils/                   # Utility functions
│
├── connectors/                  # All connectors in one place for now
│   ├── pubmed/
│   │   ├── __init__.py
│   │   ├── connector.py         # PubMed connector implementation
│   │   └── connector.yaml       # Specification file
│   ├── clinicaltrials/
│   │   ├── __init__.py
│   │   ├── connector.py
│   │   └── connector.yaml
│   └── europepmc/
│       ├── __init__.py
│       ├── connector.py
│       └── connector.yaml
│
└── tests/                       # Centralized tests
    ├── sdk/
    ├── ingestion/
    └── connectors/
```

This structure is designed to be modular, with clear boundaries between components. In the future, the connector SDK and individual connectors can be extracted into separate packages with minimal changes.

## Installation

```bash
pip install herpai-ingestion
```

## Quick Start

### Basic Usage

```python
from herpai_ingestion.services import IngestionService
from herpai_ingestion.workers import LocalProcessExecutor
import asyncio

async def main():
    # Create a local executor for direct processing
    executor = LocalProcessExecutor()
    
    # Create ingestion service
    service = IngestionService(task_executor=executor)
    
    # Run ingestion from PubMed
    result = await service.ingest_from_pubmed(
        query="herpes simplex virus treatment",
        limit=100
    )
    
    print(f"Processed {result['documents_processed']} documents")

if __name__ == "__main__":
    asyncio.run(main())
```

### CLI Usage

```bash
# Basic ingestion (processes locally)
herpai ingest --source pubmed --query "HSV1 pathogenesis" --limit 100

# Enqueue task for asynchronous processing
herpai ingest --source pubmed --query "HSV2 vaccine" --limit 100 --async

# Start a worker to process queued tasks
herpai worker start --rabbitmq-url amqp://guest:guest@localhost/

# Schedule regular ingestion
herpai scheduler add --name "daily-pubmed" --source pubmed --query "herpes zoster" --schedule "0 0 * * *"
```

## Configuration

HerpAI-Ingestion uses a YAML configuration file. You can specify the path with `--config` or use the default location at `./config.yaml`.

Example config:

```yaml
database:
  type: sqlite
  connection: ":memory:"  # In-memory SQLite database

storage:
  type: azure
  azure:
    account_name: your_account_name
    account_key: your_account_key
    container_name: herpai-datalake
    prefix: documents/
  
connectors:
  pubmed:
    api_key: your_api_key
    batch_size: 100
  europepmc:
    enabled: true
  clinicaltrials:
    enabled: true

rabbitmq:
  host: localhost
  port: 5672
  username: guest
  password: guest
  
scheduler:
  enabled: true
  jobs:
    - source: pubmed
      query: "herpes simplex virus"
      schedule: "0 1 * * *"  # Daily at 1 AM
      limit: 1000
```

## Connector Specifications

Each connector includes a YAML specification file (`connector.yaml`) that defines its capabilities, configuration options, and behavior:

```yaml
# Example connector.yaml for PubMed
name: pubmed
display_name: PubMed
description: Connects to the PubMed biomedical literature database
version: 1.0.0

capabilities:
  supports_fulltext: false
  supports_advanced_search: true
  supports_date_filtering: true

api:
  base_url: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
  rate_limit:
    requests_per_second: 3
    with_api_key: 10

pagination:
  type: token-based
  default_batch_size: 100
  max_batch_size: 200

configuration:
  properties:
    - name: api_key
      type: string
      required: false
      description: NCBI API key for higher rate limits
    - name: batch_size
      type: integer
      required: false
      default: 100
      description: Number of items to retrieve in each batch
```

These specifications serve multiple purposes:
- **Documentation**: Clear description of connector capabilities
- **Validation**: Ensure connectors implement required features
- **Code Generation**: Auto-generate connector skeletons
- **Configuration**: Define configuration options and validation rules

## Creating a New Connector

To create a new connector for a data source:

1. **Create a directory** in the `connectors/` folder:
   ```
   connectors/new_source/
   ```

2. **Create a specification file** (`connector.yaml`) defining the connector's capabilities:
   ```yaml
   name: new_source
   display_name: New Source
   description: Connects to the New Source API
   version: 1.0.0
   
   capabilities:
     supports_fulltext: false
     supports_advanced_search: true
     
   # Other specifications...
   ```

3. **Implement the connector** by subclassing `BaseConnector`:
   ```python
   # connectors/new_source/connector.py
   from herpai_connector_sdk.base import BaseConnector
   from herpai_connector_sdk.interfaces import Document
   
   class NewSourceConnector(BaseConnector):
       @property
       def name(self) -> str:
           return "new_source"
       
       @property
       def version(self) -> str:
           return "1.0.0"
       
       @property
       def source_name(self) -> str:
           return "New Source"
       
       async def search(self, query, limit=None):
           # Implementation...
           pass
       
       async def get_by_id(self, id):
           # Implementation...
           pass
   ```

4. **Add tests** for your connector:
   ```python
   # tests/connectors/test_new_source.py
   import pytest
   from connectors.new_source.connector import NewSourceConnector
   
   @pytest.mark.asyncio
   async def test_new_source_connector(connector_tester):
       connector = NewSourceConnector()
       await connector_tester.test_basic_functionality(
           connector, 
           query="herpes simplex virus"
       )
   ```

The connector will be automatically discovered and registered when the ingestion system starts.

## System Workflow

The following sequence diagrams illustrate the key workflows in the HerpAI-Ingestion system:

### 1. Task Submission Workflow

This diagram shows what happens when a user or scheduler submits an ingestion task:

```mermaid
sequenceDiagram
    participant User as User/Scheduler
    participant CLI as CLI
    participant Service as Ingestion Service
    participant Queue as RabbitMQ
    participant DB as Database

    User->>CLI: herpai ingest --source pubmed --query "HSV1" --async
    CLI->>Service: ingest_from_pubmed("HSV1", async=True)
    Service->>DB: Create ingestion job record
    DB-->>Service: Return job ID
    Service->>Queue: Publish task to "ingestion_tasks" queue
    Queue-->>Service: Confirm message received
    Service-->>CLI: Return job ID
    CLI-->>User: Display job ID and status
```

### 2. Worker Processing Workflow

This diagram shows what happens when a worker processes a task:

```mermaid
sequenceDiagram
    participant Worker as Worker Process
    participant Queue as RabbitMQ
    participant Executor as Task Executor
    participant Connector as Source Connector
    participant API as External API
    participant Repo as Document Repository

    Queue->>Worker: Deliver next task from queue
    Worker->>Executor: execute_task("PubMed", {"query": "HSV1"})
    Executor->>Connector: Create connector for PubMed
    
    loop For each batch of results
        Connector->>API: Request documents matching "HSV1"
        API-->>Connector: Return matching documents
        
        loop For each document
            Connector->>Repo: Check if document exists
            alt Document is new
                Connector->>Repo: Store document
                Connector->>Queue: Publish processing task
            end
        end
    end
    
    Worker->>Queue: Acknowledge task completion
    Queue-->>Worker: Confirm acknowledgment
```

These diagrams illustrate how the system separates task submission from task processing, allowing for efficient resource usage and scalability.

## Worker Processing

The `herpai worker start` command launches worker processes that consume tasks from the message queue. Let's look at how this works in both local and Kubernetes environments:

### RabbitMQ vs Worker Roles

It's important to understand the distinct roles in this architecture:

- **RabbitMQ**: Acts purely as a message broker. It doesn't process any data itself - it only receives, stores, and delivers messages to workers. Think of it as a task distribution system that ensures work is properly routed and tracked.

- **Worker Processes**: These are separate processes that do the actual work. They connect to RabbitMQ to retrieve tasks, then perform all the processing (connecting to APIs, downloading documents, data transformation, storage operations). All the heavy lifting happens in these workers, not in RabbitMQ.

### Understanding Worker Processing

When you run `herpai worker start --rabbitmq-url amqp://guest:guest@localhost/`, you're starting a worker process that:

1. Connects to RabbitMQ
2. Subscribes to the task queue
3. Waits for incoming tasks
4. Processes each task as it arrives

Each worker process can handle multiple task types (PubMed, ClinicalTrials, etc.) and multiple tasks sequentially. The system is designed so that a single worker can process all types of tasks from any source.

### Local Environment

In a local environment, you can:

1. Start one or more worker processes:
```bash
# Start a worker in one terminal
herpai worker start --rabbitmq-url amqp://guest:guest@localhost/

# Start another worker in another terminal if needed
herpai worker start --rabbitmq-url amqp://guest:guest@localhost/
```

2. Submit tasks through the CLI or API:
```bash
# These tasks will be distributed to available workers
herpai ingest --source pubmed --query "HSV1" --async
herpai ingest --source clinicaltrials --query "HSV2" --async
```

3. Workers pick up tasks in a first-come, first-served basis
4. If one worker is busy, tasks go to other available workers
5. If all workers are busy, tasks wait in the queue

### Kubernetes Environment

In Kubernetes, workers run as pods in a deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: herpai-worker
spec:
  replicas: 3  # Run 3 worker pods
  selector:
    matchLabels:
      app: herpai-worker
  template:
    metadata:
      labels:
        app: herpai-worker
    spec:
      containers:
      - name: worker
        image: herpai-ingestion:latest
        command: ["python", "-m", "herpai_ingestion.cli", "worker", "start"]
        env:
        - name: RABBITMQ_URL
          value: "amqp://guest:guest@rabbitmq-service:5672/"
```

With this deployment:

1. You have 3 worker pods running simultaneously
2. Each pod consumes tasks from the same RabbitMQ queue
3. RabbitMQ distributes tasks across available workers
4. If a pod fails, Kubernetes restarts it
5. You can scale up/down the number of workers as needed:
```bash
kubectl scale deployment herpai-worker --replicas=5
```

## Deployment Models

HerpAI-Ingestion supports multiple deployment models:

### Local Development

Run everything locally for development and testing:

```bash
# Start RabbitMQ (optional)
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management

# Start workers locally
herpai worker start

# Run ingestion
herpai ingest --source pubmed --query "HSV transmission" --async
```

### Docker Compose

For a self-contained deployment:

```yaml
# docker-compose.yml
version: '3'

services:
  rabbitmq:
    image: rabbitmq:management
    ports:
      - "5672:5672"
      - "15672:15672"
  
  api:
    image: herpai-ingestion:latest
    command: python -m herpai_ingestion.api
    ports:
      - "8000:8000"
    environment:
      - RABBITMQ_HOST=rabbitmq
    volumes:
      - ./config.yaml:/app/config.yaml
  
  worker:
    image: herpai-ingestion:latest
    command: python -m herpai_ingestion.cli worker start
    environment:
      - RABBITMQ_HOST=rabbitmq
    volumes:
      - ./config.yaml:/app/config.yaml
```

### Kubernetes

For production environments:

```bash
# Deploy using Helm
helm install herpai-ingestion ./charts/herpai-ingestion
```

The Kubernetes deployment includes:
- API server deployment
- Worker deployment
- RabbitMQ StatefulSet (or external service)
- Configuration via ConfigMaps and Secrets

## Development

### Prerequisites

- Python 3.9+
- RabbitMQ (optional, for distributed processing)
- HerpAI-CoreLib

### Setting Up Development Environment

1. Clone the repository
   ```bash
   git clone https://github.com/openbiocure/HerpAI-Ingestion.git
   cd HerpAI-Ingestion
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -e ".[dev]"
   ```

4. Run tests
   ```bash
   pytest
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.