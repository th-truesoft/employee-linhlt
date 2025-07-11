## Cài đặt

### Phương pháp 1: Sử dụng Docker (Khuyến nghị)

```bash
# Build và khởi động container
docker-compose up -d --build

# Kiểm tra logs
docker-compose logs -f
```

API sẽ chạy tại http://localhost:8000

### Phương pháp 2: Cài đặt thủ công

#### 1. Tạo môi trường ảo

```bash
python -m venv .venv
source .venv/bin/activate  # Trên Windows: .venv\Scripts\activate
```

#### 2. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

#### 3. Tạo file môi trường

Copy file `.env.example` thành `.env`:

```bash
cp .env.example .env
```

#### 4. Tạo bảng cho database

```bash
python create_tables.py
```

#### 5. Tạo dữ liệu mẫu

```bash
python -m app.db.init_script
```

#### 6. Start app

```bash
uvicorn app.main:app --reload
```

#### 7. Kiểm tra API

```bash
python test_api.py
```

#### 8. Code coverage and pytest

```bash
python run_tests.py
```

## Api docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Xác thực

API sử dụng cơ chế xác thực token bearer đơn giản. Tất cả các endpoint API đều yêu cầu header `Authorization` với token bearer:

```
Authorization: Bearer employee-directory-api-token
```

Token mặc định được cấu hình trong file `.env` dưới dạng `DEFAULT_API_TOKEN`. Bạn nên thay đổi giá trị này thành một giá trị an toàn hơn trong môi trường sản xuất.

### Các Endpoint chính

#### API Tìm kiếm Nhân viên

```
POST /api/v1/employees/search
```
**Request Body:**

```json
{
  "status": ["active", "inactive"],
  "location_ids": [1, 2],
  "department_ids": [1],
  "position_ids": [1, 2],
  "name": "Employee",
  "page": 1,
  "page_size": 20,
  "columns": ["name", "email", "department", "position"]
}
```

**Query Parameters:**

- `organization_id`: ID của tổ chức để sử dụng cho cấu hình cột (mặc định: "default")

**Response:**

```json
{
  "items": [
    {
      "name": "Nguyen Van A",
      "email": "nguyenvana@example.com",
      "department": "Engineering",
      "position": "Software Engineer"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "pages": 1,
  "columns": ["name", "email", "department", "position"]
}
```
## Cấu hình column theo tổ chức

API hỗ trợ cấu hình column động cho từng tổ chức. Điều này được quản lý thông qua module `organization_config.py`, có thể được mở rộng để sử dụng cơ sở dữ liệu hoặc dịch vụ cấu hình bên ngoài trong môi trường sản xuất.

Ví dụ cấu hình:

```json
{
  "default": {
    "columns": ["name", "email", "phone", "status", "department", "position", "location"]
  },
  "org1": {
    "columns": ["name", "email", "department", "position"]
  },
  "org2": {
    "columns": ["name", "status", "department", "location"]
  }
}
```

## Rate limit

Rate limit được cấu hình thông qua các biến môi trường:

- `RATE_LIMIT`: Số lượng yêu cầu tối đa được phép trong RATE_LIMIT_WINDOW_SIZE (mặc định: 100)
- `RATE_LIMIT_WINDOW_SIZE`: Default: 60s

## Kiểm thử

### Chạy test với pytest

```bash
pytest
```

### Chạy test với coverage

```bash
python run_tests.py
```

Báo cáo coverage sẽ được tạo trong thư mục `coverage_reports/html`.
