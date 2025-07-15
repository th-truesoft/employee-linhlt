# 🚀 Getting Started Guide

## Guide for new users of Employee Directory API

### 📋 **Prerequisites**

```bash
# 1. Python 3.11+
python --version  # Should be 3.11 or higher

# 2. Git
git --version

# 3. Virtual Environment (recommended)
python -m venv --help
```

---

## 🏁 **Step 1: Clone & Setup Project**

```bash
# Clone project (if from git)
git clone <repository-url>
cd demo-employee-ts

# Or if you already have project folder
cd demo-employee-ts
```

---

## 🐍 **Step 2: Setup Python Environment**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Verify virtual environment
which python  # Should point to venv/bin/python
```

---

## 📦 **Step 3: Install Dependencies**

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
pip list | grep uvicorn
```

---

## 🗄️ **Step 4: Setup Database**

### **Option A: Automatic Setup (Recommended)**

```bash
# One command setup everything
make setup

# This will:
# ✅ Install dependencies
# ✅ Create database tables
# ✅ Setup OAuth2
# ✅ Generate JWT tokens
```

### **Option B: Manual Setup**

```bash
# 1. Create database tables
python scripts/create_tables.py

# 2. Setup OAuth2 tables
python scripts/create_oauth2_tables.py

# 3. Generate JWT tokens
python scripts/generate_jwt_token.py
```

---

## 🚀 **Step 5: Start the Application**

### **Option A: Using Makefile (Recommended)**

```bash
# Start development server
make dev

# Server will start at http://localhost:8000
```

### **Option B: Direct Python**

```bash
# Start server directly
python main.py
```

### **Option C: Using uvicorn**

```bash
# Start with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## ✅ **Step 6: Verify Everything Works**

### **1. Check Server Status**

```bash
# Test health endpoint
curl http://localhost:8000/health
# Expected: {"status":"healthy",...}
```

### **2. Access API Documentation**

Mở browser và vào:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **3. Test Basic Endpoints**

```bash
# Test OAuth2 scopes
curl http://localhost:8000/api/v1/oauth2/scopes

# Test detailed health
curl http://localhost:8000/api/v1/monitoring/health/detailed
```

---

## 🔐 **Step 7: Test Authentication**

### **1. Get JWT Token**

```bash
# JWT tokens have been generated in config/jwt_tokens.json
cat config/jwt_tokens.json
```

### **2. Test Authenticated Endpoints**

```bash
# Copy token từ jwt_tokens.json (organization: default)
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Test employee search với authentication
curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -X POST \
     -d '{"q": "test", "filters": {}}' \
     http://localhost:8000/api/v1/employees/search
```

---

## 📊 **Step 8: Explore Features**

### **Available Endpoints:**

- `GET /health` - Basic health check
- `GET /docs` - API documentation
- `GET /api/v1/oauth2/scopes` - OAuth2 scopes
- `POST /api/v1/employees/search` - Employee search
- `GET /api/v1/monitoring/health/detailed` - Detailed monitoring
- `GET /api/v1/monitoring/dashboard` - System dashboard

### **Test Some Features:**

```bash
# 1. View all OAuth2 scopes
curl http://localhost:8000/api/v1/oauth2/scopes | jq

# 2. Check system monitoring
curl http://localhost:8000/api/v1/monitoring/health/detailed | jq

# 3. View system dashboard
curl http://localhost:8000/api/v1/monitoring/dashboard | jq
```

---

## 🛠️ **Development Commands**

```bash
# Show all available commands
make help

# Start development server
make dev

# Run tests
make test

# Initialize database
make init-db

# Generate new JWT tokens
make tokens

# Clean temporary files
make clean
```

---

## 🧪 **Testing the API**

### **1. Using Swagger UI (Easy)**

1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Enter: `Bearer <your-jwt-token>`
4. Test any endpoint directly

### **2. Using curl commands**

```bash
# Get JWT token
TOKEN=$(cat config/jwt_tokens.json | jq -r '.default.token')

# Test employee search
curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -X POST \
     -d '{"q": "developer", "filters": {"department": "Engineering"}}' \
     http://localhost:8000/api/v1/employees/search | jq

# Test advanced search
curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -X POST \
     -d '{"query": "senior developer", "filters": {}, "limit": 10}' \
     http://localhost:8000/api/v1/employees/advanced-search | jq
```

### **3. Using Postman/Insomnia**

1. Import OpenAPI spec: http://localhost:8000/api/v1/openapi.json
2. Set Authorization: Bearer Token
3. Use token from `config/jwt_tokens.json`

---

## 🚨 **Troubleshooting**

### **Common Issues:**

#### **1. Port already in use**

```bash
# Kill existing server
pkill -f "python main.py"
# Or
lsof -ti:8000 | xargs kill -9
```

#### **2. Database issues**

```bash
# Reset database
rm *.db
make init-db
```

#### **3. Permission issues**

```bash
# Fix permissions
chmod +x scripts/*.py
```

#### **4. Import errors**

```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

#### **5. JWT token expired**

```bash
# Generate new tokens
make tokens
# Or
python scripts/generate_jwt_token.py
```

---

## 📁 **Project Structure Overview**

```
demo-employee-ts/
├── 📄 main.py                    # Entry point
├── 📄 Makefile                   # Development commands
├── 📁 app/                       # Main application code
│   ├── api/endpoints/            # API endpoints
│   ├── core/                     # Core functionality
│   ├── models/                   # Database models
│   └── services/                 # Business logic
├── 📁 scripts/                   # Utility scripts
├── 📁 config/                    # Configuration files
├── 📁 docs/                      # Documentation
└── 📁 tests/                     # Test files
```

---

## 🎯 **Next Steps**

1. **Explore API**: Play with different endpoints in Swagger UI
2. **Read Documentation**: Check files in `docs/` folder
3. **Add Sample Data**: Run `scripts/init_async_db.py` for test data
4. **Enable Redis**: Follow `docs/PROJECT_IMPROVEMENTS_REPORT.md` Redis section
5. **Deploy**: Use `docker-compose up -d` for production-like setup

---

## 💡 **Tips for New Developers**

1. **Always use virtual environment** để tránh conflict packages
2. **Check logs** khi có lỗi: server sẽ print detailed error messages
3. **Use Swagger UI** để test API interactively
4. **JWT tokens expire in 24h** - generate new ones khi cần
5. **Redis optional** - app works fine without it
6. **Check `make help`** để xem all available commands

---

## 📞 **Getting Help**

- Check server logs for detailed error messages
- Use Swagger UI at http://localhost:8000/docs để test endpoints
- View project documentation in `docs/` folder
- All configuration in `config/` folder
- JWT tokens in `config/jwt_tokens.json`

**Happy coding! 🎉**
