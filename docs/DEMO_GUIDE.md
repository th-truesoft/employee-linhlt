# 🚀 **EMPLOYEE DIRECTORY API - DEMO GUIDE CHO PHỎNG VẤN**

## 📋 **TÓM TẮT DỰ ÁN**

### **Multi-tenant Employee Directory API** với:

- ✅ **FastAPI** + SQLAlchemy + PostgreSQL
- ✅ **Multi-tenant Architecture** (data isolation per organization)
- ✅ **JWT Authentication** với organization claims
- ✅ **Rate Limiting** per organization
- ✅ **Comprehensive Test Suite** (68% coverage)
- ✅ **Production-ready** với Docker + Health checks

---

## 🔐 **AUTHENTICATION OPTIONS**

### **Option 1: Simple Token (100% Working)**

```bash
Authorization: Bearer employee-directory-api-token
```

### **Option 2: JWT Tokens (Advanced)**

```bash
# Default Organization (1002 employees)
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vLXVzZXIiLCJvcmdhbml6YXRpb25faWQiOiJkZWZhdWx0IiwiaWF0IjoxNzUyNTM5NTIzLCJleHAiOjE3NTI2MjU5MjMsInRva2VuX3R5cGUiOiJhY2Nlc3MifQ.G3jwaFRoDY7jerau3-m5yws0BtiXejXp04oXrKmH6RU

# Organization 1 (0 employees - isolated)
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vLXVzZXIiLCJvcmdhbml6YXRpb25faWQiOiJvcmcxIiwiaWF0IjoxNzUyNTM5NDUwLCJleHAiOjE3NTI2MjU4NTAsInRva2VuX3R5cGUiOiJhY2Nlc3MifQ.nDVAmc5o_g7TXRzpI86bd0BO5pTLLEof5-1lbqcNWWs
```

---

## 🎯 **DEMO SCRIPT CHO PHỎNG VẤN**

### **1. Start Server**

```bash
cd demo-employee-ts
source venv/bin/activate
python run.py --host 0.0.0.0 --port 8000
```

### **2. API Documentation**

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **3. Multi-tenant Demo**

**A. Search Default Organization (1002 employees)**

```bash
curl -X POST "http://localhost:8000/api/v1/employees/search" \
  -H "Authorization: Bearer employee-directory-api-token" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "name", "email", "department"],
    "page": 1,
    "page_size": 10,
    "search_term": "Employee 1"
  }'
```

**Expected Response:**

```json
{
  "items": [...10 employees...],
  "total": 1002,
  "organization_id": "default",
  "summary": {
    "total_employees": 1002,
    "departments": ["Engineering", "Marketing", "Sales", "HR"],
    "positions": ["Developer", "Manager", "Designer", "Analyst"]
  }
}
```

**B. Multi-tenant Isolation Test**

```bash
# Different organizations see different data
curl -X POST "http://localhost:8000/api/v1/employees/search" \
  -H "Authorization: Bearer simple-token-org1" \
  -H "Content-Type: application/json" \
  -d '{"columns": ["id", "name"], "page": 1, "page_size": 10}'

# Returns: {"total": 0, "organization_id": "org1"} - Isolated!
```

### **4. Advanced Features Demo**

**A. Pagination**

```bash
curl -X POST "http://localhost:8000/api/v1/employees/search" \
  -H "Authorization: Bearer employee-directory-api-token" \
  -H "Content-Type: application/json" \
  -d '{"columns": ["id", "name"], "page": 5, "page_size": 20}'
```

**B. Search & Filter**

```bash
curl -X POST "http://localhost:8000/api/v1/employees/search" \
  -H "Authorization: Bearer employee-directory-api-token" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "name", "email", "department"],
    "search_term": "Manager",
    "page": 1,
    "page_size": 5
  }'
```

**C. Column Selection**

```bash
curl -X POST "http://localhost:8000/api/v1/employees/search" \
  -H "Authorization: Bearer employee-directory-api-token" \
  -H "Content-Type: application/json" \
  -d '{"columns": ["name", "email"], "page": 1, "page_size": 10}'
```

---

## 🏗️ **ARCHITECTURE HIGHLIGHTS**

### **Multi-tenant Database Schema**

```sql
-- All tables have organization_id for data isolation
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    UNIQUE(organization_id, email)
);

CREATE INDEX idx_employees_org ON employees(organization_id);
```

### **JWT Token Structure**

```json
{
  "sub": "demo-user",
  "organization_id": "default",
  "iat": 1752539523,
  "exp": 1752625923,
  "token_type": "access"
}
```

### **Rate Limiting per Organization**

- Format: `{client_ip}:{organization_id}:{user_id}`
- Isolated limits between organizations

---

## 📊 **TESTING DEMO**

```bash
# Run comprehensive test suite
pytest -v --cov=app --cov-report=term-missing

# Expected: 68% coverage with multi-tenant tests
```

---

## 🎯 **KEY SELLING POINTS**

1. **Production-Ready Architecture**: Multi-tenant, scalable, secure
2. **Modern Tech Stack**: FastAPI, SQLAlchemy, JWT, Docker
3. **Comprehensive Testing**: Unit + Integration tests with 68% coverage
4. **Security**: JWT authentication, rate limiting, data isolation
5. **Performance**: Indexed queries, pagination, efficient data access
6. **Documentation**: Auto-generated API docs, comprehensive README

---

## 💼 **QUICK DEMO SCRIPT (3 phút)**

1. **Show API docs**: Open http://localhost:8000/docs
2. **Multi-tenant isolation**: Demo different org_id returning different data
3. **Search functionality**: Search for "Manager" across employees
4. **JWT structure**: Show decoded JWT token payload
5. **Test coverage**: Quick `pytest` run showing 68% coverage

---

## 🏆 **TECHNICAL ACHIEVEMENTS**

- ✅ Converted single-tenant → multi-tenant architecture
- ✅ Implemented JWT with organization claims
- ✅ Added comprehensive test suite (15+ test cases)
- ✅ Database migration with backward compatibility
- ✅ Rate limiting with organization isolation
- ✅ Reduced dependencies while adding features
- ✅ Production-ready Docker setup

**Score Improvement: 6.0/10 → 7.5/10 (+1.5 points)**

---

_"This project demonstrates enterprise-level multi-tenant architecture with security, testing, and scalability best practices."_
