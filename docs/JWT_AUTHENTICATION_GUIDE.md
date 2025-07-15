# 🔐 JWT Authentication Guide

After removing OAuth2, the API now only uses **JWT (JSON Web Token)** authentication. This is a detailed guide on how to get and use JWT tokens.

## 🎯 **1. Create JWT Token**

### **Method 1: Use existing script**

```bash
python scripts/generate_jwt_token.py
```

This script will create tokens for 4 organizations:

- `default` - Organization mặc định
- `org1` - Company A
- `org2` - Company B
- `enterprise` - Enterprise Corp

### **Output mẫu:**

```
📋 Default Organization (org_id: default)
JWT Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vLXVzZXI...
Authorization Header: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Method 2: Create custom token with Python**

```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key-here-change-in-production"

def create_jwt_token(organization_id: str, user_id: str = "demo-user"):
    payload = {
        "sub": user_id,
        "organization_id": organization_id,
        "iat": int(datetime.utcnow().timestamp()),
        "exp": int((datetime.utcnow() + timedelta(hours=24)).timestamp()),
        "token_type": "access"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Create token for organization "default"
token = create_jwt_token("default")
print(f"Token: {token}")
```

## 🚀 **2. Use Token in API Calls**

### **2.1. cURL Examples**

#### **Employee Search:**

```bash
# Set token variable
JWT_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vLXVzZXI..."

# Search employees
curl -X POST \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"search_term":"john","limit":10}' \
  http://localhost:8000/api/v1/employees/search
```

#### **Advanced Search:**

```bash
curl -X POST \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "search_term": "manager",
    "department": "IT",
    "status": "active",
    "limit": 20
  }' \
  http://localhost:8000/api/v1/employees/advanced-search
```

#### **Health Check (không cần auth):**

```bash
curl http://localhost:8000/api/v1/monitoring/health/detailed
```

### **2.2. Python Requests**

```python
import requests

JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vLXVzZXI..."
BASE_URL = "http://localhost:8000/api/v1"

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

# Employee search
response = requests.post(
    f"{BASE_URL}/employees/search",
    headers=headers,
    json={"search_term": "developer", "limit": 5}
)

if response.status_code == 200:
    data = response.json()
    print(f"Found {data['total']} employees")
    print(f"Organization: {data['organization_id']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### **2.3. JavaScript/Axios**

```javascript
const axios = require("axios");

const JWT_TOKEN =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vLXVzZXI...";
const BASE_URL = "http://localhost:8000/api/v1";

const headers = {
  Authorization: `Bearer ${JWT_TOKEN}`,
  "Content-Type": "application/json",
};

// Employee search
async function searchEmployees() {
  try {
    const response = await axios.post(
      `${BASE_URL}/employees/search`,
      { search_term: "sales", limit: 10 },
      { headers }
    );

    console.log(`Found ${response.data.total} employees`);
    console.log(`Organization: ${response.data.organization_id}`);
  } catch (error) {
    console.error("API Error:", error.response?.data || error.message);
  }
}

searchEmployees();
```

## 🌐 **3. Use with Swagger UI**

1. Mở trình duyệt: `http://localhost:8000/docs`
2. Click nút **"Authorize"** ở đầu trang
3. Nhập token theo format: `Bearer <JWT_TOKEN>`
4. Click **"Authorize"**
5. Bây giờ có thể test tất cả endpoints có authentication

## 🔍 **4. Multi-Tenant Support**

Mỗi JWT token chứa `organization_id`, API sẽ tự động filter data theo organization:

### **Token cho organization khác nhau:**

```bash
# Default organization
JWT_DEFAULT="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vLXVzZXI..."

# Company A (org1)
JWT_ORG1="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vLXVzZXI..."

# Test với organization khác nhau
curl -H "Authorization: Bearer $JWT_DEFAULT" \
     http://localhost:8000/api/v1/employees/search

curl -H "Authorization: Bearer $JWT_ORG1" \
     http://localhost:8000/api/v1/employees/search
```

## ⏰ **5. Token Expiration**

- **Thời gian sống:** 24 giờ (1440 minutes)
- **Algorithm:** HS256
- **When expired:** Create new token using script

### **Kiểm tra token còn hiệu lực:**

```python
import jwt
from datetime import datetime

SECRET_KEY = "your-secret-key-here-change-in-production"
token = "your-jwt-token-here"

try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    exp_time = datetime.fromtimestamp(payload['exp'])
    print(f"Token expires at: {exp_time}")
    print(f"Organization: {payload['organization_id']}")
    print(f"User: {payload['sub']}")
except jwt.ExpiredSignatureError:
    print("Token đã hết hạn!")
except jwt.InvalidTokenError:
    print("Token không hợp lệ!")
```

## ❌ **6. Troubleshooting**

### **Lỗi thường gặp:**

#### **`"detail": "Authorization header is missing"`**

```bash
# ❌ Sai - thiếu Authorization header
curl -X POST http://localhost:8000/api/v1/employees/search

# ✅ Đúng
curl -H "Authorization: Bearer $JWT_TOKEN" \
     -X POST http://localhost:8000/api/v1/employees/search
```

#### **`"detail": "Invalid authentication scheme"`**

```bash
# ❌ Sai - thiếu "Bearer "
curl -H "Authorization: $JWT_TOKEN" ...

# ✅ Đúng
curl -H "Authorization: Bearer $JWT_TOKEN" ...
```

#### **`"detail": "Invalid token"`**

- Token bị sai format
- Token đã hết hạn
- SECRET_KEY không match
- Token bị truncated/corrupted

#### **`"detail": "Token missing organization_id claim"`**

- Token was created without `organization_id`
- Need to regenerate token with official script

## 📁 **7. Lưu Token**

Tokens được lưu tự động tại: `config/jwt_tokens.json`

```json
{
  "default": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "organization_id": "default",
    "expires_at": "2025-07-16T10:17:43Z"
  },
  "org1": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "organization_id": "org1",
    "expires_at": "2025-07-16T10:17:43Z"
  }
}
```

## 🔒 **8. Security Best Practices**

1. **Không share token:** Mỗi client/user nên có token riêng
2. **Rotate tokens:** Create new tokens periodically (before expiration)
3. **Secure storage:** Lưu token trong environment variables, không hardcode
4. **HTTPS only:** Production phải dùng HTTPS
5. **Validate expiration:** Check token expiry before using

## ✅ **9. Quick Test Commands**

```bash
# 1. Generate token
python scripts/generate_jwt_token.py

# 2. Copy token từ output (dòng JWT Token:)
JWT_TOKEN="paste-token-here"

# 3. Test API
curl -H "Authorization: Bearer $JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"search_term":"test"}' \
     http://localhost:8000/api/v1/employees/search

# 4. Expected response với empty database:
# {"items":[],"total":0,"organization_id":"default",...}
```

---

🎉 **Complete!** Now you know how to use JWT authentication for the API.
