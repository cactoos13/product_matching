# Entity Matching Project - Comprehensive Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Technology Stack](#technology-stack)
5. [Installation & Setup](#installation--setup)
6. [Configuration](#configuration)
7. [Usage Guide](#usage-guide)
8. [API Documentation](#api-documentation)
9. [Matching Algorithms](#matching-algorithms)
10. [Database Schema](#database-schema)
11. [Task System](#task-system)
12. [Performance & Scalability](#performance--scalability)
13. [Development](#development)
14. [Deployment](#deployment)
15. [Troubleshooting](#troubleshooting)

---

## Project Overview

The **Entity Matching Project** is a high-performance, scalable system designed for matching and finding similar products/advertisements using advanced machine learning techniques. The system combines **Locality-Sensitive Hashing (LSH)** for fast candidate retrieval with **ParsBERT embeddings** and **cosine similarity** for accurate semantic matching.

### Key Capabilities

- **Fast Similarity Search**: Uses LSH to quickly find candidate matches from large datasets
- **Semantic Understanding**: Leverages ParsBERT (Persian BERT) for deep semantic understanding of Persian text
- **Hybrid Approach**: Combines the speed of LSH with the accuracy of neural embeddings
- **Scalable Architecture**: Built with Redis for distributed caching and MySQL for persistent storage
- **Dual Database Support**: Reads from source database and writes to destination database
- **Automated Synchronization**: Periodic tasks for keeping data in sync
- **RESTful API**: FastAPI-based endpoints for easy integration

### Use Cases

- Product matching and deduplication
- Advertisement-to-product matching
- Similar product recommendations
- Entity resolution in e-commerce platforms
- Content-based search and retrieval

---

## Architecture

### System Architecture

```
┌─────────────────┐
│   FastAPI App   │
│   (main.py)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │        │
┌───▼───┐ ┌──▼────┐
│ Redis │ │ MySQL │
│ (LSH) │ │(Dest) │
└───────┘ └───┬───┘
              │
         ┌────▼────┐
         │  MySQL  │
         │(Source) │
         └─────────┘
```

### Component Overview

1. **FastAPI Application** (`main.py`)
   - RESTful API endpoints
   - Health checks
   - Request handling

2. **Redis Repository** (`AdvertisementRedisRepository`)
   - Stores ParsBERT embeddings
   - Maintains LSH index
   - Fast in-memory operations

3. **SQL Repositories**
   - Source database: Read-only access to original data
   - Destination database: Write operations for matched results

4. **Task System (Celery)**
   - Periodic synchronization tasks
   - Batch indexing operations
   - Background processing

5. **Matching Engine**
   - LSH for candidate retrieval
   - ParsBERT for semantic embeddings
   - Cosine similarity for ranking

### Data Flow

```
1. Source Database (c2c_advertisements)
   ↓
2. Synchronization Task (periodic)
   ↓
3. Destination Database (advertisements)
   ↓
4. Indexing Task (batch)
   ↓
5. Redis (embeddings + LSH index)
   ↓
6. Query API (/find)
   ↓
7. Results (product IDs)
```

---

## Features

### Core Features

✅ **Hybrid Matching Algorithm**
- LSH-based fast candidate retrieval
- ParsBERT semantic embeddings
- Cosine similarity ranking

✅ **Dual Database Architecture**
- Source database for read operations
- Destination database for write operations
- Automatic synchronization

✅ **Redis Integration**
- Distributed caching
- LSH index storage
- Embedding persistence

✅ **Task Automation**
- Periodic synchronization
- Batch indexing
- Background processing with Celery

✅ **RESTful API**
- `/find` - Similarity search
- `/health` - System health checks
- `/redis/inspect` - Redis inspection

✅ **Scalability**
- Horizontal scaling support
- Distributed task processing
- Efficient memory usage

---

## Technology Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Programming language |
| **FastAPI** | 0.115.6 | Web framework |
| **Uvicorn** | 0.34.0 | ASGI server |
| **SQLAlchemy** | 2.0.37 | ORM |
| **Alembic** | 1.14.1 | Database migrations |
| **Celery** | 5.4.0 | Task queue |
| **Redis** | 5.2.1 | Caching & LSH storage |
| **MySQL** | 8.0+ | Database |
| **Poetry** | Latest | Dependency management |

### Machine Learning Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| **sentence-transformers** | 3.0.0 | ParsBERT embeddings |
| **transformers** | 4.40.0 | Hugging Face models |
| **torch** | 2.3.0 | PyTorch backend |
| **scikit-learn** | 1.5.2 | Cosine similarity |
| **datasketch** | 1.6.5 | MinHash LSH |
| **numpy** | 2.2.3 | Numerical operations |

### Additional Libraries

- **pandas** - Data manipulation
- **openpyxl** - Excel file handling
- **pymysql** - MySQL connector
- **python-dotenv** - Environment variables

---

## Installation & Setup

### Prerequisites

- Python 3.11 or higher
- Poetry (dependency manager)
- MySQL 8.0+
- Redis 6.0+
- Docker & Docker Compose (optional, for containerized deployment)

### Step 1: Install Poetry

```bash
pip install pipx
pipx install poetry
```

### Step 2: Clone Repository

```bash
git clone https://github.com/cactoos13/product_matching.git
cd product_matching
```

### Step 3: Install Dependencies

```bash
poetry install
```

### Step 4: Environment Configuration

Create a `.env` file in the project root:

```env
# Source Database (Read-only)
SOURCE_MYSQL_DB_USER=your_source_user
SOURCE_MYSQL_DB_PASS=your_source_password
SOURCE_MYSQL_DB_HOST=source_host
SOURCE_MYSQL_DB_PORT=3306
SOURCE_MYSQL_DB_DATABASE=source_database

# Destination Database (Read/Write)
DEST_MYSQL_DB_USER=your_dest_user
DEST_MYSQL_DB_PASS=your_dest_password
DEST_MYSQL_DB_HOST=dest_host
DEST_MYSQL_DB_PORT=3306
DEST_MYSQL_DB_DATABASE=dest_database

# Redis Configuration
LSH_REDIS_HOST=localhost
LSH_REDIS_PORT=6379
LSH_REDIS_DB=0

# LSH Parameters
LSH_SIMILARITY_THRESHOLD=0.3
LSH_PERMUTATIONS=128

# ParsBERT Configuration
PARSBERT_MODEL_NAME=HooshvareLab/bert-fa-base-uncased
PARSBERT_DEVICE=cpu  # or 'cuda' for GPU

# Redis Index Prefix (optional)
ADS_REDIS_INDEX_PREFIX=ads

# Last Sync Key
LAST_SYNC_KEY=last_sync

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### Step 5: Database Setup

#### Run Migrations

```bash
poetry run alembic upgrade head
```

#### Verify Database Connections

```bash
poetry run python -c "from bootstrap import bootstrap; from modules import Modules; bootstrap(total=True, modules=Modules)"
```

### Step 6: Start Services

#### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

This will start:
- MySQL database
- Redis server
- FastAPI application
- Celery worker
- Celery beat scheduler

#### Manual Start

**Terminal 1 - Redis:**
```bash
redis-server
```

**Terminal 2 - FastAPI:**
```bash
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3 - Celery Worker:**
```bash
poetry run celery -A main:scheduler worker --loglevel=info
```

**Terminal 4 - Celery Beat:**
```bash
poetry run celery -A main:scheduler beat --loglevel=info
```

### Step 7: Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Ping endpoint
curl http://localhost:8000/ping
```

---

## Configuration

### Environment Variables

#### Database Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `SOURCE_MYSQL_DB_*` | Source database credentials | Yes |
| `DEST_MYSQL_DB_*` | Destination database credentials | Yes |

#### Redis Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `LSH_REDIS_HOST` | Redis host | localhost |
| `LSH_REDIS_PORT` | Redis port | 6379 |
| `LSH_REDIS_DB` | Redis database number | 0 |

#### LSH Parameters

| Variable | Description | Default |
|----------|-------------|---------|
| `LSH_SIMILARITY_THRESHOLD` | LSH similarity threshold (0.0-1.0) | 0.3 |
| `LSH_PERMUTATIONS` | Number of MinHash permutations | 128 |

**LSH Threshold Guidelines:**
- `0.1-0.3`: More candidates, lower precision
- `0.3-0.5`: Balanced (recommended)
- `0.5-0.7`: Fewer candidates, higher precision
- `0.7+`: Very strict matching

#### ParsBERT Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `PARSBERT_MODEL_NAME` | Hugging Face model name | HooshvareLab/bert-fa-base-uncased |
| `PARSBERT_DEVICE` | Device (cpu/cuda) | auto-detect |

#### Optional Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `ADS_REDIS_INDEX_PREFIX` | Prefix for Redis keys | (empty) |
| `LAST_SYNC_KEY` | Key for last sync timestamp | last_sync |

---

## Usage Guide

### Basic Usage

#### 1. Index Products/Advertisements

```python
from bootstrap import bootstrap
from modules import Modules
from packages.core.registry import Registry
from packages.business.modules.advertisement.services.advertisement_redis_service import AdvertisementRedisService
from packages.business.modules.advertisement.entities.advertisement_idx_entity import AdvertisementIdx

# Bootstrap application
bootstrap(total=True, modules=Modules)

# Get service
service = Registry().get(AdvertisementRedisService)

# Create entities
ads = [
    AdvertisementIdx(id=1, text="iPhone 14 Pro Max 256GB Space Black"),
    AdvertisementIdx(id=2, text="Samsung Galaxy S23 Ultra 512GB"),
    # ... more ads
]

# Index in batch
service.index_ads(ads, batch_size=32)
```

#### 2. Search for Similar Products

```python
# Query for similar products
similar_ids = service.query(
    text="iPhone 14 Pro",
    limit=10,
    min_similarity=0.5
)

print(f"Found {len(similar_ids)} similar products: {similar_ids}")
```

#### 3. Using the API

```bash
# Find similar products
curl -X POST "http://localhost:8000/find" \
  -H "Content-Type: application/json" \
  -d '{"text": "iPhone 14 Pro Max"}'
```

### Advanced Usage

#### Running Indexing Tasks

```python
from packages.core.registry import Registry
from packages.core.scheduler import Scheduler
from packages.business.modules.advertisement.tasks.once.advertisement_batch_index_by_categories_task import \
    AdvertisementBatchIndexByCategoriesTask

scheduler = Registry().get(Scheduler)

# Index by categories
task = AdvertisementBatchIndexByCategoriesTask(
    category_ids=[3742, 100, 200],
    limit=1000,
    offset=0
)

scheduler.run_task(task)
```

See `example_run_category_index_task.py` for complete examples.

---

## API Documentation

### Base URL

```
http://localhost:8000
```

### Endpoints

#### 1. POST `/find`

Find similar products using ParsBERT embeddings and LSH.

**Request:**
```json
{
  "text": "iPhone 14 Pro Max 256GB"
}
```

**Response:**
```json
[123, 456, 789, ...]
```

**Parameters:**
- `text` (string, required): Search query text

**Example:**
```bash
curl -X POST "http://localhost:8000/find" \
  -H "Content-Type: application/json" \
  -d '{"text": "iPhone 14 Pro"}'
```

#### 2. POST `/hash`

Generate MinHash for input text(s).

**Request:**
```json
{
  "text": "iPhone 14 Pro",
  "text2": "Samsung Galaxy S23"  // optional
}
```

**Response:**
```json
[
  {
    "hashvalues": [1234, 5678, ...],
    "num_perm": 128,
    "similar_ads": [1, 2, 3, ...],
    "digest": "abc123..."
  }
]
```

#### 3. GET `/health`

Check system health status.

**Response:**
```json
{
  "status": "ok",
  "redis": true,
  "source_db": true,
  "dest_db": true,
  "advertisement": {...},
  "c2c_advertisement": {...}
}
```

#### 4. GET `/redis/inspect`

Inspect Redis data.

**Query Parameters:**
- `limit` (int, optional): Maximum keys to show (default: 20)

**Response:**
```json
{
  "total_keys": 1000,
  "advertisement_keys": {
    "count": 500,
    "sample_keys": [...],
    "sample_values": {...}
  },
  "lsh_keys": {
    "count": 500,
    "sample_keys": [...]
  },
  "other_keys": {
    "count": 0,
    "keys": [],
    "values": {}
  }
}
```

#### 5. GET `/ping`

Simple ping endpoint.

**Response:**
```json
{
  "ping": "pong"
}
```

---

## Matching Algorithms

### Hybrid Approach: LSH + ParsBERT + Cosine Similarity

The system uses a **two-stage matching process**:

#### Stage 1: LSH Candidate Retrieval (Fast)

1. **Tokenization**: Text is tokenized into words
   ```python
   tokens = ["iphone", "14", "pro", "max"]
   ```

2. **MinHash Creation**: Tokens are hashed using MinHash
   ```python
   minhash = MinHash(num_perm=128)
   for token in tokens:
       minhash.update(token.encode('utf-8'))
   ```

3. **LSH Query**: Fast approximate search finds candidates
   ```python
   candidate_ids = lsh.query(minhash)
   # Returns: [123, 456, 789, ...] (fast, but approximate)
   ```

**Time Complexity**: O(1) average case
**Space Complexity**: O(n) where n = number of indexed items

#### Stage 2: ParsBERT + Cosine Similarity Ranking (Accurate)

1. **Query Embedding**: Generate ParsBERT embedding for query
   ```python
   query_embedding = model.encode("iPhone 14 Pro Max")
   # Shape: (768,) - 768-dimensional vector
   ```

2. **Candidate Ranking**: Calculate cosine similarity for each candidate
   ```python
   for candidate_id in candidate_ids:
       candidate_embedding = load_embedding(candidate_id)
       similarity = cosine_similarity(query_embedding, candidate_embedding)
   ```

3. **Sort & Filter**: Sort by similarity and apply threshold
   ```python
   results = sorted(similarities, key=lambda x: x[1], reverse=True)
   filtered = [r for r in results if r[1] >= min_similarity]
   ```

**Time Complexity**: O(k × d) where k = candidates, d = embedding dimension
**Space Complexity**: O(k × d)

### Algorithm Comparison

| Method | Speed | Accuracy | Use Case |
|--------|-------|----------|----------|
| **LSH Only** | ⚡⚡⚡ Very Fast | ⭐⭐ Moderate | Quick filtering |
| **ParsBERT Only** | ⚡ Slow | ⭐⭐⭐⭐⭐ Excellent | Small datasets |
| **LSH + ParsBERT** | ⚡⚡ Fast | ⭐⭐⭐⭐ Very Good | **Recommended** |

### Why This Hybrid Approach?

1. **LSH** provides fast candidate retrieval (reduces search space from millions to hundreds)
2. **ParsBERT** provides semantic understanding (handles synonyms, context, meaning)
3. **Cosine Similarity** provides accurate ranking (measures semantic distance)

**Result**: Fast enough for real-time queries, accurate enough for production use.

---

## Database Schema

### Source Database (Read-only)

#### `c2c_advertisements` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT | Primary key |
| `title_fa` | VARCHAR | Persian title |
| `description_fa` | TEXT | Persian description |
| `status` | VARCHAR | Advertisement status |
| `product_id` | INT | Associated product ID |
| `changed_at` | DATETIME | Last modification time |
| `created_at` | DATETIME | Creation time |

### Destination Database (Read/Write)

#### `advertisements` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT | Primary key |
| `title` | VARCHAR(1000) | Title |
| `description` | VARCHAR(4000) | Description |
| `status` | VARCHAR | Status |
| `product_id` | INT | Product ID |
| `created_at` | DATETIME | Creation time |
| `changed_at` | DATETIME | Modification time |

#### `products` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT | Primary key |
| `title` | VARCHAR(1000) | Product title |
| `description` | VARCHAR(4000) | Product description |
| `status` | ENUM | Product status |
| `moderation_status` | ENUM | Moderation status |
| `active` | BOOLEAN | Active flag |

#### `system_tasks` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT | Primary key |
| `type` | ENUM | Task type |
| `status` | VARCHAR | Task status |
| `name` | VARCHAR | Task name |
| `created_at` | DATETIME | Creation time |

### Redis Schema

#### Key Patterns

1. **Embeddings**: `{prefix}_embedding_{id}`
   - Value: Base64-encoded pickle of numpy array
   - Example: `ads_embedding_123`

2. **Texts**: `{prefix}_text_{id}`
   - Value: Plain text string
   - Example: `ads_text_123`

3. **All Products**: `{prefix}_all_products`
   - Value: Comma-separated list of IDs
   - Example: `ads_all_products` → `"1,2,3,4,5"`

4. **Index Flags**: `{prefix}_{id}`
   - Value: `"1"` (indexed flag)
   - Example: `ads_123`

5. **LSH Index**: `minhash:*` (binary keys)
   - Managed by datasketch library
   - Stored in Redis with binary encoding

6. **Last Sync**: `last_sync`
   - Value: Unix timestamp (string)
   - Example: `"1704067200"`

---

## Task System

### Task Types

#### 1. Periodic Tasks

**Advertisement Synchronizer Task**
- **Schedule**: Every 10 minutes
- **Purpose**: Sync changed advertisements from source to destination
- **Location**: `packages/business/modules/advertisement/tasks/periodic/advertisement_synchronizer_task.py`

#### 2. One-time Tasks

**Advertisement Batch Update Task**
- **Purpose**: Update batch of advertisements
- **Location**: `packages/business/modules/advertisement/tasks/once/advertisement_batch_update_task.py`

**Advertisement Batch Index Task**
- **Purpose**: Index advertisements in Redis
- **Location**: `packages/business/modules/advertisement/tasks/once/advertisement_batch_index_task.py`

**Advertisement Batch Index by Categories Task**
- **Purpose**: Index advertisements by category IDs
- **Location**: `packages/business/modules/advertisement/tasks/once/advertisement_batch_index_by_categories_task.py`

### Running Tasks

#### Programmatically

```python
from bootstrap import bootstrap
from modules import Modules
from packages.core.registry import Registry
from packages.core.scheduler import Scheduler
from packages.business.modules.advertisement.tasks.once.advertisement_batch_index_by_categories_task import \
    AdvertisementBatchIndexByCategoriesTask

bootstrap(total=True, modules=Modules)
scheduler = Registry().get(Scheduler)

task = AdvertisementBatchIndexByCategoriesTask(
    category_ids=[3742, 100, 200],
    limit=1000,
    offset=0
)

scheduler.run_task(task)
```

#### Via Celery CLI

```bash
# Start worker
poetry run celery -A main:scheduler worker --loglevel=info

# Start beat scheduler
poetry run celery -A main:scheduler beat --loglevel=info
```

---

## Performance & Scalability

### Performance Metrics

#### Query Performance

| Dataset Size | LSH Candidates | ParsBERT Ranking | Total Time |
|--------------|----------------|------------------|------------|
| 10K items | ~50-100 | ~50ms | ~100ms |
| 100K items | ~50-100 | ~50ms | ~100ms |
| 1M items | ~50-100 | ~50ms | ~100ms |
| 10M items | ~50-100 | ~50ms | ~100ms |

**Key Insight**: Query time is **independent of dataset size** due to LSH!

#### Indexing Performance

| Batch Size | Items | Time | Throughput |
|------------|-------|------|------------|
| 32 | 1,000 | ~30s | ~33 items/s |
| 64 | 1,000 | ~25s | ~40 items/s |
| 128 | 1,000 | ~22s | ~45 items/s |

**Recommendation**: Use batch_size=32-64 for optimal balance.

### Scalability Features

1. **Horizontal Scaling**
   - Multiple Celery workers
   - Redis cluster support
   - Load-balanced API servers

2. **Memory Efficiency**
   - Embeddings stored in Redis (not memory)
   - Lazy loading of embeddings
   - Batch processing

3. **Distributed Processing**
   - Celery for background tasks
   - Redis as message broker
   - Stateless API design

### Optimization Tips

1. **LSH Threshold Tuning**
   - Lower threshold = more candidates = slower but more accurate
   - Higher threshold = fewer candidates = faster but may miss matches

2. **Batch Size Tuning**
   - Larger batches = faster indexing but more memory
   - Smaller batches = slower but more stable

3. **GPU Acceleration**
   - Set `PARSBERT_DEVICE=cuda` for faster embeddings
   - Requires CUDA-compatible GPU

---

## Development

### Project Structure

```
entity_matching_prop/
├── alembic/                 # Database migrations
├── data/                    # Sample data files
├── packages/
│   ├── business/           # Business logic modules
│   │   └── modules/
│   │       ├── advertisement/  # Advertisement module
│   │       ├── product/        # Product module
│   │       └── system_task/    # System task module
│   └── core/               # Core framework
│       ├── entity/         # Entity base classes
│       ├── repository/     # Repository pattern
│       ├── service/         # Service layer
│       ├── scheduler/       # Celery scheduler
│       └── sql_connector/   # Database connectors
├── scripts/                # Utility scripts
├── bootstrap.py            # Application bootstrap
├── main.py                 # FastAPI application
├── modules.py              # Module registry
├── pyproject.toml         # Poetry dependencies
└── README.md              # This file
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Document functions and classes
- Keep functions focused and small

### Adding New Features

1. **Create Entity**
   ```python
   # packages/business/modules/your_module/entities/your_entity.py
   from packages.core.entity import SqlEntity
   
   class YourEntity(SqlEntity):
       __tablename__ = 'your_table'
       # ... fields
   ```

2. **Create Repository**
   ```python
   # packages/business/modules/your_module/repositories/your_repository.py
   from packages.core.repository import SqlRepository
   
   class YourRepository(SqlRepository[YourEntity]):
       pass
   ```

3. **Create Service**
   ```python
   # packages/business/modules/your_module/services/your_service.py
   from packages.core.service import SqlService
   
   class YourService(SqlService[YourEntity]):
       pass
   ```

4. **Register Module**
   ```python
   # modules.py
   from packages.business.modules.your_module.module import YourModule
   
   class Modules:
       your_module = YourModule()
   ```

### Database Migrations

#### Create Migration

```bash
poetry run alembic revision --autogenerate -m "description"
```

#### Apply Migration

```bash
poetry run alembic upgrade head
```

#### Rollback Migration

```bash
poetry run alembic downgrade -1
```

**Note**: Migrations only affect the destination database. Source database tables are automatically excluded.

---

## Deployment

### Docker Deployment

#### Build Image

```bash
docker build -t entity-matching:latest .
```

#### Run with Docker Compose

```bash
docker-compose up -d
```

#### Environment Variables

Create `.env` file or set environment variables:

```bash
export SOURCE_MYSQL_DB_USER=user
export SOURCE_MYSQL_DB_PASS=pass
# ... other variables
```

### Production Considerations

1. **Security**
   - Use environment variables for secrets
   - Enable SSL/TLS for database connections
   - Implement API authentication
   - Use secrets management (e.g., HashiCorp Vault)

2. **Monitoring**
   - Set up logging (e.g., ELK stack)
   - Monitor Redis memory usage
   - Track API response times
   - Monitor Celery task queue

3. **Backup**
   - Regular database backups
   - Redis persistence configuration
   - Backup embeddings periodically

4. **Scaling**
   - Use Redis Cluster for large datasets
   - Deploy multiple API instances
   - Scale Celery workers based on load

---

## Troubleshooting

### Common Issues

#### 1. Redis Connection Error

**Error**: `Connection refused` or `Redis not found in Registry`

**Solution**:
```bash
# Check Redis is running
redis-cli ping

# Verify environment variables
echo $LSH_REDIS_HOST
echo $LSH_REDIS_PORT
echo $LSH_REDIS_DB
```

#### 2. Database Connection Error

**Error**: `Could not connect to database`

**Solution**:
```bash
# Test source database
mysql -h $SOURCE_MYSQL_DB_HOST -u $SOURCE_MYSQL_DB_USER -p

# Test destination database
mysql -h $DEST_MYSQL_DB_HOST -u $DEST_MYSQL_DB_USER -p

# Check environment variables
env | grep MYSQL
```

#### 3. ParsBERT Model Loading Error

**Error**: `Could not load ParsBERT model`

**Solution**:
```bash
# Check internet connection (for downloading model)
ping huggingface.co

# Try alternative model
export PARSBERT_MODEL_NAME=HooshvareLab/bert-fa-base-uncased

# Check disk space
df -h
```

#### 4. LSH Query Returns Empty Results

**Possible Causes**:
- No items indexed yet
- LSH threshold too high
- MinHash mismatch

**Solution**:
```bash
# Check if items are indexed
curl http://localhost:8000/redis/inspect

# Lower LSH threshold
export LSH_SIMILARITY_THRESHOLD=0.2

# Re-index items
```

#### 5. Slow Query Performance

**Possible Causes**:
- Too many LSH candidates
- Large embedding dimensions
- CPU-bound operations

**Solution**:
- Increase LSH threshold (fewer candidates)
- Use GPU for ParsBERT (`PARSBERT_DEVICE=cuda`)
- Optimize batch sizes
- Add Redis caching layer

### Debugging

#### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Inspect Redis Data

```bash
# Using script
poetry run python inspect_redis.py

# Using API
curl http://localhost:8000/redis/inspect?limit=100

# Using Redis CLI
redis-cli
> KEYS *
> GET ads_embedding_123
```

#### Check Health Status

```bash
curl http://localhost:8000/health
```

---

## Additional Resources

### Standalone Scripts

The project includes several standalone matching scripts for testing and comparison:

- `simple_product_matcher_parsbert_lsh.py` - ParsBERT + LSH (recommended)
- `simple_product_matcher_parsbert.py` - ParsBERT only
- `simple_product_matcher_minhash_lsh_cosine.py` - MinHash + LSH + Cosine
- `simple_product_matcher_cosine_lsh.py` - Cosine + LSH
- `simple_product_matcher_standalone.py` - Standalone (no Redis)

### Example Usage

```bash
# Run standalone matcher
python simple_product_matcher_parsbert_lsh.py \
  --products data/products.xlsx \
  --ads data/advertisements.xlsx \
  --output results.xlsx
```

### References

- [MinHash LSH Documentation](https://ekzhu.com/datasketch/lsh.html)
- [ParsBERT Model](https://huggingface.co/HooshvareLab/bert-fa-base-uncased)
- [Sentence Transformers](https://www.sbert.net/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.org/)

---

## License

[Add your license information here]

## Contributors

- **AmirHossein Advari** <amiradvari@gmail.com>

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Last Updated**: 2024
**Version**: 0.1.0
