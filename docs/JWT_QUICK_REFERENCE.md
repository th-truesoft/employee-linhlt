# 🔐 JWT Authentication - Quick Reference

## 🚀 **Step 1: Create Token**

```bash
python scripts/generate_jwt_token.py
```

## 🔑 **Bước 2: Copy Token**

```
JWT Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vLXVzZXI...
```

## 🌐 **Step 3: Use Token**

### **cURL:**

```bash
JWT_TOKEN="your-token-here"

curl -X POST \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"search_term":"test"}' \
  http://localhost:8000/api/v1/employees/search
```

### **Python:**

```python
import requests

headers = {"Authorization": "Bearer your-token-here"}
requests.post("http://localhost:8000/api/v1/employees/search",
              headers=headers, json={"search_term": "test"})
```

### **Swagger UI:**

1. `http://localhost:8000/docs`
2. Click **"Authorize"**
3. Enter: `Bearer your-token-here`

## 📊 **Available Endpoints (with JWT):**

- `POST /api/v1/employees/search` - Search employees
- `POST /api/v1/employees/advanced-search` - Advanced search
- `GET /api/v1/employees/search-suggestions` - Search suggestions

## 🚫 **No Auth Required:**

- `GET /api/v1/monitoring/health/detailed` - Health check
- `GET /api/v1/monitoring/metrics/*` - Monitoring metrics

## ⚡ **Quick Test:**

```bash
# 1. Generate token
python scripts/generate_jwt_token.py

# 2. Test API (replace token)
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     -H "Content-Type: application/json" \
     -d '{"search_term":"test"}' \
     http://localhost:8000/api/v1/employees/search

# 3. Expected: {"items":[],"total":0,"organization_id":"default",...}
```

## 🔄 **Token Info:**

- **Duration:** 24 hours
- **Format:** `Bearer <JWT_TOKEN>`
- **Algorithm:** HS256
- **Multi-tenant:** Yes (organization_id in payload)

## ❌ **Common Errors:**

- `"Authorization header is missing"` → Add `-H "Authorization: Bearer $TOKEN"`
- `"Invalid authentication scheme"` → Must start with `Bearer `
- `"Invalid token"` → Token expired/corrupted, generate new one
