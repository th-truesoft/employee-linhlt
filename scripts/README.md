# Scripts Directory

This directory contains utility scripts for the Employee Directory API project.

## 🚀 **Application Scripts**

### `run.py`

**Main application runner**

```bash
python scripts/run.py
```

- Starts the FastAPI application with uvicorn
- Configurable host, port, and reload options
- Development-friendly with auto-reload

## 🔧 **Setup & Database Scripts**

### `create_tables.py`

**Database initialization**

```bash
python scripts/create_tables.py
```

- Creates basic database tables
- Sets up initial schema
- Safe to run multiple times

### `create_oauth2_tables.py`

**OAuth2 tables setup**

```bash
python scripts/create_oauth2_tables.py
```

- Creates OAuth2 security tables
- Initializes default scopes
- Generates demo OAuth2 client
- **Run after** `create_tables.py`

### `init_async_db.py`

**Async database initialization**

```bash
python scripts/init_async_db.py
```

- Initializes async database with sample data
- Creates demo employees, departments, positions
- Use for testing async endpoints

## 🔐 **Authentication Scripts**

### `generate_jwt_token.py`

**JWT token generator**

```bash
python scripts/generate_jwt_token.py
```

- Generates JWT tokens for different organizations
- Creates tokens for testing multi-tenant features
- Outputs tokens to `config/jwt_tokens.json`

### `generate_token.py`

**Simple token generator**

```bash
python scripts/generate_token.py
```

- Generates simple API tokens
- Backward compatibility support
- Quick testing utility

## 🧪 **Testing Scripts**

### `run_tests.py`

**Test runner with coverage**

```bash
python scripts/run_tests.py
```

- Runs full test suite with pytest
- Generates coverage reports
- Creates HTML coverage reports in `coverage_reports/`

## 📋 **Usage Order**

For new setup:

```bash
# 1. Create basic tables
python scripts/create_tables.py

# 2. Set up OAuth2 security
python scripts/create_oauth2_tables.py

# 3. Generate test tokens
python scripts/generate_jwt_token.py

# 4. Start application
python scripts/run.py

# 5. Run tests
python scripts/run_tests.py
```

## 🔗 **Dependencies**

All scripts assume:

- Virtual environment is activated
- Requirements are installed (`pip install -r requirements.txt`)
- Running from project root directory
