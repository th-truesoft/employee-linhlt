# Quick Start Guide

Get the Employee Directory API up and running in minutes!

## 🚀 5-Minute Setup

### Option 1: Docker (Recommended)

**Prerequisites:** Docker and Docker Compose installed

```bash
# 1. Clone the repository
git clone <repository-url>
cd demo-employee-ts

# 2. Start the application
docker-compose up -d

# 3. Check if it's running
curl http://localhost:8000/health
```

**That's it!** Your API is running at http://localhost:8000

### Option 2: Manual Setup

**Prerequisites:** Python 3.11+

```bash
# 1. Clone and setup
git clone <repository-url>
cd demo-employee-ts
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install and initialize
pip install -r requirements.txt
python create_tables.py
python -m app.db.init_script

# 3. Start the server
python run.py
```

## 🧪 Test Your Installation

### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Expected Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "redis": { "status": "disconnected" },
  "rate_limiting": { "backend": "memory" }
}
```

### 2. Interactive Documentation

Open your browser: http://localhost:8000/docs

### 3. Search Employees

```bash
curl -X POST "http://localhost:8000/api/v1/employees/search" \
  -H "Authorization: Bearer employee-directory-api-token" \
  -H "Content-Type: application/json" \
  -d '{"page": 1, "page_size": 5}'
```

**Expected Response:**

```json
{
  "items": [
    {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice.johnson@company.com",
      "status": "active",
      "department": "Engineering"
    }
  ],
  "total": 1002,
  "page": 1,
  "page_size": 5
}
```

## 🏢 Multi-Tenant Example

### Generate JWT Token

```bash
python generate_jwt_token.py
```

**Output:**

```
Organization: org1
JWT Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Use JWT Token

```bash
# Replace <JWT_TOKEN> with the generated token
curl -X POST "http://localhost:8000/api/v1/employees/search" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"page": 1, "page_size": 3}'
```

## ⚡ Performance Testing

### Async Endpoints

```bash
# Test high-performance async search
curl -X POST "http://localhost:8000/api/v1/async/employees/search" \
  -H "Authorization: Bearer employee-directory-api-token" \
  -H "Content-Type: application/json" \
  -d '{"page": 1, "page_size": 10}'
```

### Rate Limiting

```bash
# Check rate limit status
curl http://localhost:8000/api/v1/rate-limit-info \
  -H "organization-id: org1"
```

## 🔧 Configuration

### Environment Variables

Create `.env` file for custom settings:

```env
# Basic Configuration
RATE_LIMIT=100
RATE_LIMIT_WINDOW_SIZE=60
SECRET_KEY=your-secret-key

# Redis (Optional)
REDIS_RATE_LIMITING=true
REDIS_URL=redis://localhost:6379/0

# Database
SQLITE_DB=employee_directory.db
```

### With Redis

To enable distributed rate limiting:

```bash
# Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Enable Redis in environment
export REDIS_RATE_LIMITING=true
export REDIS_URL=redis://localhost:6379/0

# Restart application
python run.py
```

## 📊 Sample Data

The application comes with sample data:

- **1002 employees** in "default" organization
- **Multiple departments:** Engineering, Marketing, Sales, HR
- **Various positions:** Engineer, Manager, Director, etc.
- **Multiple locations:** New York, San Francisco, London

### Search Examples

```bash
# Search by name
curl -X POST "http://localhost:8000/api/v1/employees/search" \
  -H "Authorization: Bearer employee-directory-api-token" \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "page_size": 3}'

# Filter by status
curl -X POST "http://localhost:8000/api/v1/employees/search" \
  -H "Authorization: Bearer employee-directory-api-token" \
  -H "Content-Type: application/json" \
  -d '{"status": ["active"], "page_size": 5}'

# Custom columns
curl -X POST "http://localhost:8000/api/v1/employees/search" \
  -H "Authorization: Bearer employee-directory-api-token" \
  -H "Content-Type: application/json" \
  -d '{"columns": ["name", "email", "department"], "page_size": 3}'
```

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│     Client      │────│   FastAPI App    │────│    Database     │
│                 │    │                  │    │   (SQLite)      │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ HTTP Client │ │    │ │ Rate Limiter │ │    │ │ Multi-tenant│ │
│ │ (curl/JS)   │ │    │ │ (Memory)     │ │    │ │ Data        │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
└─────────────────┘    │ ┌──────────────┐ │    └─────────────────┘
                       │ │ Async Engine │ │
                       │ │ (Optional)   │ │
                       │ └──────────────┘ │
                       └──────────────────┘
```

## 🛠️ Development Workflow

### Running Tests

```bash
# Install test dependencies (already in requirements.txt)
pip install pytest pytest-cov pytest-asyncio

# Run all tests
python run_tests.py

# Run specific test
pytest tests/api/test_employee_api.py -v
```

### Code Quality

```bash
# Format code
pip install black
black app/ tests/

# Check linting
pip install flake8
flake8 app/
```

### Database Operations

```bash
# Reset database
rm employee_directory.db
python create_tables.py
python -m app.db.init_script

# Check database
sqlite3 employee_directory.db ".tables"
```

## 🐳 Docker Development

### Development with Live Reload

```yaml
# docker-compose.dev.yml
version: "3.8"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - PYTHONPATH=/app
      - RELOAD=true
```

```bash
docker-compose -f docker-compose.dev.yml up
```

### Production Setup

```bash
# Production with Redis
docker-compose up -d

# Check logs
docker-compose logs -f api
docker-compose logs -f redis
```

## 🔍 Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

#### Database Issues

```bash
# Reset everything
rm employee_directory.db
python create_tables.py
python -m app.db.init_script
```

#### Module Import Errors

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### Redis Connection Issues

```bash
# Check if Redis is running
redis-cli ping

# Start Redis with Docker
docker run -d -p 6379:6379 redis:7-alpine

# Disable Redis if not needed
export REDIS_RATE_LIMITING=false
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python run.py

# Check logs
tail -f app.log
```

## 📚 Next Steps

1. **Read the full documentation:** [README_EN.md](../README_EN.md)
2. **Explore API endpoints:** [API_REFERENCE_EN.md](API_REFERENCE_EN.md)
3. **Set up production deployment:** [DEPLOYMENT_EN.md](DEPLOYMENT_EN.md)
4. **Configure multi-tenancy:** See Multi-Tenant section in main README
5. **Enable Redis:** Follow Redis configuration guide
6. **Add monitoring:** Set up health checks and logging

## 🤝 Getting Help

- **Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Rate Limit Info:** http://localhost:8000/api/v1/rate-limit-info
- **GitHub Issues:** [Create an issue](https://github.com/your-repo/issues)

## 🎯 Quick Commands Reference

```bash
# Start application
python run.py

# Run tests
python run_tests.py

# Generate JWT tokens
python generate_jwt_token.py

# Health check
curl http://localhost:8000/health

# Search employees
curl -X POST "http://localhost:8000/api/v1/employees/search" \
  -H "Authorization: Bearer employee-directory-api-token" \
  -H "Content-Type: application/json" \
  -d '{"page": 1}'

# Rate limit info
curl http://localhost:8000/api/v1/rate-limit-info

# Interactive docs
open http://localhost:8000/docs
```

---

**Happy coding!** 🚀
