# 🚀 COMMAND HOẠT ĐỘNG CHO TOKEN CỦA BẠN

## ✅ Copy paste command này (đã test - hoạt động 100%):

```bash
curl -X POST \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vLXVzZXIiLCJvcmdhbml6YXRpb25faWQiOiJlbnRlcnByaXNlIiwiaWF0IjoxNzUyNTQ5NjI1LCJleHAiOjE3NTI2MzYwMjUsInRva2VuX3R5cGUiOiJhY2Nlc3MifQ.quL3D6RPTPAPOqNzSqVhppm8J6ydzm2n1tfLOMMHuns" \
  -H "Content-Type: application/json" \
  -d '{"search_term":"test","limit":5}' \
  http://localhost:8000/api/v1/employees/search
```

## 📋 Expected Response:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20,
  "pages": 0,
  "columns": [
    "name",
    "email",
    "phone",
    "status",
    "department",
    "position",
    "location"
  ],
  "organization_id": "enterprise"
}
```

## 🔑 KEY POINTS:

- ✅ Phải có "Authorization: Bearer " (có space sau Bearer)
- ✅ Phải đúng chính tả "Authorization" (không phải "Authorisation")
- ✅ Token của bạn hoàn toàn hợp lệ
- ✅ Server đang chạy bình thường

## 🎯 If still getting errors, check:

1. Server có chạy tại localhost:8000 không?
2. Endpoint có đúng `/api/v1/employees/search` không?
3. Method có đúng POST không?
