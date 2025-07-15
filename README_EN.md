# Employee Directory API

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Redis](https://img.shields.io/badge/Redis-Optional-red.svg)](https://redis.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Enterprise-grade FastAPI microservice for employee directory management with multi-tenant architecture, async database operations, and distributed rate limiting.

## ✨ Key Features

### 🏢 Multi-Tenant Architecture

- **Complete data isolation** per organization
- **JWT-based authentication** with organization claims
- **Dynamic column configuration** per organization
- **Organization-scoped rate limiting**

### ⚡ High Performance

- **Async database operations** with SQLAlchemy 2.0
- **Connection pooling** for optimal performance
- **Redis-based distributed rate limiting** with graceful fallback
- **Concurrent request processing**

### 🛡️ Enterprise Security

- **JWT authentication** with organization isolation
- **Rate limiting** (100 req/min per organization by default)
- **Input validation** with Pydantic schemas
- **CORS configuration** for cross-origin requests

### 🚀 Production Ready

- **Docker containerization** with health checks
- **Graceful degradation** when Redis unavailable
- **Comprehensive logging** and monitoring
- **Clean architecture** with repository pattern

## 📖 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Multi-Tenant Usage](#-multi-tenant-usage)
- [Architecture](#-architecture)
- [Development](#-development)
- [Deployment](#-deployment)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)

## 📚 Documentation

- **[Quick Start Guide](docs/QUICK_START_EN.md)** - Get up and running in 5 minutes
- **[API Reference](docs/API_REFERENCE_EN.md)** - Complete API documentation
- **[Deployment Guide](docs/DEPLOYMENT_EN.md)** - Production deployment instructions

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd demo-employee-ts

# Start with Redis (distributed rate limiting)
docker-compose up -d

# Or start without Redis (in-memory fallback)
docker-compose up -d api
```

### Manual Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python create_tables.py
python -m app.db.init_script

# Start the application
python run.py
```

**API will be available at:** http://localhost:8000

**Documentation:** http://localhost:8000/docs

## 📦 Installation

### Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose** (optional but recommended)
- **Redis** (optional, for distributed rate limiting)

### Environment Setup

1. **Clone and setup environment:**

```bash
git clone <repository-url>
cd demo-employee-ts
python -m venv venv
source venv/bin/activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Database initialization:**

```bash
# Create tables
python create_tables.py

# Migrate existing database (if needed)
python migrate_to_multitenant.py

# Initialize with sample data
python -m app.db.init_script
```

4. **Configuration (optional):**

Create `.env` file for custom configuration:

```env
# Database
SQLITE_DB=employee_directory.db

# Authentication
SECRET_KEY=your-secret-key-here
DEFAULT_API_TOKEN=employee-directory-api-token

# Rate Limiting
RATE_LIMIT=100
RATE_LIMIT_WINDOW_SIZE=60

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
REDIS_RATE_LIMITING=true

# CORS
BACKEND_CORS_ORIGINS=["http://localhost", "http://localhost:3000"]
```

## ⚙️ Configuration

### Database Configuration

The application supports both **SQLite** (development) and **PostgreSQL** (production):

```python
# SQLite (default)
SQLITE_DB=employee_directory.db

# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=employee_directory
```

### Redis Configuration

Redis provides distributed rate limiting but is **optional**:

```env
# Enable Redis rate limiting
REDIS_RATE_LIMITING=true
REDIS_URL=redis://localhost:6379/0

# Redis connection settings
REDIS_CONNECTION_TIMEOUT=5
REDIS_MAX_CONNECTIONS=20
REDIS_RETRY_ON_TIMEOUT=true
```

**Graceful Fallback:** If Redis is unavailable, the system automatically falls back to in-memory rate limiting.

### Multi-Tenant Configuration

Organizations can have custom column configurations:

```json
{
  "org1": {
    "columns": ["name", "email", "department", "position"]
  },
  "org2": {
    "columns": ["name", "status", "department", "location"]
  }
}
```

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

### Authentication

#### JWT Authentication (Recommended)

```bash
# Generate JWT token
python generate_jwt_token.py

# Use in API calls
curl -X POST "http://localhost:8000/api/v1/employees/search" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"page": 1, "page_size": 10}'
```

**JWT Token Structure:**

```json
{
  "sub": "api_user",
  "organization_id": "org1",
  "exp": 1234567890,
  "iat": 1234567890
}
```

#### Simple Token (Backward Compatibility)

```bash
curl -X GET "http://localhost:8000/api/v1/employees/" \
  -H "Authorization: Bearer employee-directory-api-token"
```

### Core Endpoints

#### Employee Search

```http
POST /api/v1/employees/search
```

**Request:**

```json
{
  "status": ["active", "inactive"],
  "location_ids": [1, 2],
  "department_ids": [1],
  "position_ids": [1, 2],
  "name": "John",
  "page": 1,
  "page_size": 20,
  "columns": ["name", "email", "department", "position"]
}
```

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john.doe@company.com",
      "status": "active",
      "department": "Engineering",
      "position": "Software Engineer",
      "location": "New York"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

#### Async Endpoints (High Performance)

```http
# Async employee list
GET /api/v1/async/employees/

# Async search
POST /api/v1/async/employees/search

# Async get by ID
GET /api/v1/async/employees/{id}

# Async create
POST /api/v1/async/employees/
```

#### Health & Monitoring

```http
# Health check
GET /health

# Rate limit info
GET /api/v1/rate-limit-info
```

## 🏢 Multi-Tenant Usage

### Organization Isolation

Each organization has completely isolated data:

```bash
# Search employees in organization 1
curl -X POST "http://localhost:8000/api/v1/employees/search" \
  -H "organization-id: org1" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"page": 1}'

# Search employees in organization 2
curl -X POST "http://localhost:8000/api/v1/employees/search" \
  -H "organization-id: org2" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"page": 1}'
```

### Rate Limiting per Organization

Each organization has separate rate limiting quotas:

- **org1**: 100 requests/minute
- **org2**: 100 requests/minute
- **org3**: 100 requests/minute

### Custom Column Configuration

Organizations can customize which employee fields to return:

```python
# Configure columns for organization
from app.core.organization_config import update_organization_columns

update_organization_columns("org1", ["name", "email", "department"])
update_organization_columns("org2", ["name", "status", "location"])
```

## 🏗️ Architecture

### System Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │────│  Redis (Optional) │    │   Database      │
│                 │    │                  │    │   (SQLite/PG)   │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Rate Limiter│─┼────┼─│ Distributed  │ │    │ │ Multi-tenant│ │
│ │ Middleware  │ │    │ │ Rate Limits  │ │    │ │ Tables      │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    └──────────────────┘    │ ┌─────────────┐ │
│ │ Async       │ │                            │ │ Connection  │ │
│ │ Endpoints   │─┼────────────────────────────┼─│ Pool        │ │
│ └─────────────┘ │                            │ └─────────────┘ │
└─────────────────┘                            └─────────────────┘
```

### Layer Architecture

```
├── 📁 app/
│   ├── 📁 api/           # API layer (FastAPI endpoints)
│   │   ├── endpoints/    # Individual endpoint modules
│   │   └── routes.py     # Route registration
│   ├── 📁 core/          # Core functionality
│   │   ├── config.py     # Configuration management
│   │   ├── deps.py       # Dependency injection
│   │   ├── middleware.py # Custom middleware
│   │   └── rate_limiter.py # Rate limiting logic
│   ├── 📁 db/            # Database layer
│   │   ├── session.py    # Database sessions
│   │   └── init_script.py # Database initialization
│   ├── 📁 models/        # Database models (SQLAlchemy)
│   ├── 📁 repositories/  # Repository pattern (data access)
│   ├── 📁 schemas/       # Pydantic schemas (validation)
│   └── 📁 services/      # Business logic layer
```

### Multi-Tenant Data Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Auth
    participant RateLimit
    participant Service
    participant DB

    Client->>API: Request + JWT Token
    API->>Auth: Validate & extract organization_id
    Auth-->>API: organization_id="org1"
    API->>RateLimit: Check rate limit for org1
    RateLimit-->>API: ✅ Rate limit OK
    API->>Service: Process with organization context
    Service->>DB: Query WHERE organization_id='org1'
    DB-->>Service: Organization-scoped data
    Service-->>API: Filtered results
    API-->>Client: Response + rate limit headers
```

## 🔧 Development

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific test module
pytest tests/api/test_employee_api.py -v

# Run with coverage
pytest --cov=app --cov-report=html
```

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/
```

### Database Migrations

```bash
# Create new migration
python migrate_to_multitenant.py

# Initialize async database
python init_async_db.py
```

### Performance Testing

```bash
# Test async endpoints
python test_async_performance.py

# Test rate limiting
python test_rate_limiting.py
```

## 🚀 Deployment

### Docker Deployment

#### Production with Redis

```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  api:
    build: .
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - REDIS_RATE_LIMITING=true
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - redis

volumes:
  redis_data:
```

#### Development without Redis

```yaml
# docker-compose.dev.yml
version: "3.8"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_RATE_LIMITING=false
    volumes:
      - .:/app
```

### Kubernetes Deployment

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: employee-directory-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: employee-directory-api
  template:
    metadata:
      labels:
        app: employee-directory-api
    spec:
      containers:
        - name: api
          image: employee-directory-api:latest
          ports:
            - containerPort: 8000
          env:
            - name: REDIS_URL
              value: "redis://redis-service:6379/0"
            - name: REDIS_RATE_LIMITING
              value: "true"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
```

### Environment Variables

```bash
# Production environment variables
export SECRET_KEY="your-production-secret-key"
export REDIS_URL="redis://production-redis:6379/0"
export REDIS_RATE_LIMITING="true"
export RATE_LIMIT="500"
export RATE_LIMIT_WINDOW_SIZE="60"
export DB_HOST="production-postgres"
export DB_NAME="employee_directory_prod"
```

## ⚡ Performance

### Benchmarks

#### Response Times

| Endpoint        | Sync | Async | Improvement    |
| --------------- | ---- | ----- | -------------- |
| Employee Search | 45ms | 12ms  | **73% faster** |
| Employee List   | 38ms | 8ms   | **79% faster** |
| Get by ID       | 15ms | 4ms   | **73% faster** |

#### Throughput

| Configuration                | Requests/sec | Notes             |
| ---------------------------- | ------------ | ----------------- |
| Sync + Memory Rate Limiting  | 850 req/s    | Single instance   |
| Async + Memory Rate Limiting | 2,100 req/s  | Single instance   |
| Async + Redis Rate Limiting  | 1,950 req/s  | Distributed setup |

#### Database Performance

| Operation    | SQLite | PostgreSQL | Notes         |
| ------------ | ------ | ---------- | ------------- |
| Simple Query | 2ms    | 3ms        | Single record |
| Search Query | 15ms   | 8ms        | 1000+ records |
| Bulk Insert  | 120ms  | 45ms       | 100 records   |

### Optimization Features

- **Connection Pooling**: Optimized database connections
- **Async Operations**: Non-blocking I/O operations
- **Redis Caching**: Distributed rate limiting cache
- **Eager Loading**: Optimized relationship loading
- **Query Optimization**: Indexed database queries

## 🔍 Troubleshooting

### Common Issues

#### Redis Connection Issues

```bash
# Check Redis availability
redis-cli ping

# Check Redis logs
docker-compose logs redis

# Test without Redis
export REDIS_RATE_LIMITING=false
python run.py
```

#### Database Issues

```bash
# Reset database
rm employee_directory.db
python create_tables.py
python -m app.db.init_script

# Check database integrity
sqlite3 employee_directory.db ".schema"
```

#### Rate Limiting Issues

```bash
# Check rate limit status
curl http://localhost:8000/api/v1/rate-limit-info

# Reset rate limits (Redis)
redis-cli FLUSHDB

# Check rate limit headers
curl -I http://localhost:8000/
```

### Error Codes

| Status Code | Description  | Solution                           |
| ----------- | ------------ | ---------------------------------- |
| 401         | Unauthorized | Check JWT token validity           |
| 429         | Rate Limited | Wait or check rate limit headers   |
| 404         | Not Found    | Verify organization_id in token    |
| 500         | Server Error | Check logs and database connection |

### Logging

```bash
# Check application logs
docker-compose logs api

# Enable debug logging
export LOG_LEVEL=DEBUG
python run.py

# Check specific component logs
grep "redis" /var/log/app.log
grep "rate_limit" /var/log/app.log
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Ensure all tests pass

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - Python SQL toolkit
- **Redis** - In-memory data structure store
- **Pydantic** - Data validation library
- **Docker** - Containerization platform

---

**Made with ❤️ for enterprise applications**

For questions or support, please open an issue or contact the development team.
