# API Reference

This document provides detailed information about all available endpoints in the Employee Directory API.

## Base URL

```
https://your-domain.com/api/v1
```

## Authentication

### JWT Authentication (Recommended)

Include JWT token in the Authorization header:

```http
Authorization: Bearer <JWT_TOKEN>
```

**JWT Token Payload:**

```json
{
  "sub": "api_user",
  "organization_id": "org1",
  "exp": 1234567890,
  "iat": 1234567890
}
```

### Simple Token (Legacy)

```http
Authorization: Bearer employee-directory-api-token
```

### Organization Header

For organization-specific requests, include:

```http
organization-id: org1
```

## Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": {},
  "message": "Operation successful",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {}
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Endpoints

### Employee Management

#### Search Employees

Search employees with filters and pagination.

```http
POST /employees/search
```

**Headers:**

- `Authorization: Bearer <token>` (required)
- `Content-Type: application/json`
- `organization-id: <org_id>` (optional)

**Request Body:**

```json
{
  "status": ["active", "inactive"],
  "location_ids": [1, 2, 3],
  "department_ids": [1, 2],
  "position_ids": [1, 2, 3],
  "name": "John",
  "page": 1,
  "page_size": 20,
  "columns": ["name", "email", "department", "position", "location"]
}
```

**Parameters:**

| Field            | Type           | Required | Description                            |
| ---------------- | -------------- | -------- | -------------------------------------- |
| `status`         | array[string]  | No       | Employee status filter                 |
| `location_ids`   | array[integer] | No       | Location IDs to filter by              |
| `department_ids` | array[integer] | No       | Department IDs to filter by            |
| `position_ids`   | array[integer] | No       | Position IDs to filter by              |
| `name`           | string         | No       | Search by name or email                |
| `page`           | integer        | No       | Page number (default: 1)               |
| `page_size`      | integer        | No       | Items per page (default: 20, max: 100) |
| `columns`        | array[string]  | No       | Specific columns to return             |

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
      "location": "New York",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

**Status Codes:**

- `200 OK` - Success
- `400 Bad Request` - Invalid parameters
- `401 Unauthorized` - Invalid or missing token
- `429 Too Many Requests` - Rate limit exceeded

#### Get Employee by ID

Get a specific employee by ID.

```http
GET /employees/{employee_id}
```

**Parameters:**

| Parameter     | Type    | Required | Description |
| ------------- | ------- | -------- | ----------- |
| `employee_id` | integer | Yes      | Employee ID |

**Response:**

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@company.com",
  "phone": "+1-555-0123",
  "status": "active",
  "department": {
    "id": 1,
    "name": "Engineering",
    "description": "Software Development"
  },
  "position": {
    "id": 1,
    "name": "Software Engineer",
    "description": "Full-stack developer"
  },
  "location": {
    "id": 1,
    "name": "New York Office",
    "address": "123 Main St",
    "city": "New York",
    "country": "USA"
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**

- `200 OK` - Success
- `404 Not Found` - Employee not found
- `401 Unauthorized` - Invalid token

#### Create Employee

Create a new employee.

```http
POST /employees/
```

**Request Body:**

```json
{
  "name": "Jane Smith",
  "email": "jane.smith@company.com",
  "phone": "+1-555-0124",
  "status": "active",
  "department_id": 1,
  "position_id": 2,
  "location_id": 1
}
```

**Required Fields:**

- `name` (string)
- `status` (string: "active" | "inactive")

**Optional Fields:**

- `email` (string, must be unique within organization)
- `phone` (string)
- `department_id` (integer)
- `position_id` (integer)
- `location_id` (integer)

**Response:**

```json
{
  "id": 101,
  "name": "Jane Smith",
  "email": "jane.smith@company.com",
  "phone": "+1-555-0124",
  "status": "active",
  "department_id": 1,
  "position_id": 2,
  "location_id": 1,
  "organization_id": "org1",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**

- `201 Created` - Employee created successfully
- `400 Bad Request` - Invalid data
- `409 Conflict` - Email already exists

#### Update Employee

Update an existing employee.

```http
PUT /employees/{employee_id}
```

**Request Body:**

```json
{
  "name": "Jane Smith Updated",
  "email": "jane.smith.updated@company.com",
  "status": "active"
}
```

**Status Codes:**

- `200 OK` - Employee updated
- `404 Not Found` - Employee not found
- `400 Bad Request` - Invalid data

#### Delete Employee

Delete an employee.

```http
DELETE /employees/{employee_id}
```

**Status Codes:**

- `204 No Content` - Employee deleted
- `404 Not Found` - Employee not found

### Async Endpoints (High Performance)

For high-performance operations, use async endpoints:

#### Async Employee Search

```http
POST /async/employees/search
```

Same request/response format as regular search, but with optimized async operations.

#### Async Employee List

```http
GET /async/employees/
```

**Query Parameters:**

- `skip` (integer): Number of records to skip (default: 0)
- `limit` (integer): Number of records to return (default: 100, max: 1000)

#### Async Get Employee

```http
GET /async/employees/{employee_id}
```

#### Async Create Employee

```http
POST /async/employees/
```

### Department Management

#### Get Departments

Get all departments for an organization.

```http
GET /departments/
```

**Response:**

```json
[
  {
    "id": 1,
    "name": "Engineering",
    "description": "Software Development Team",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

#### Create Department

```http
POST /departments/
```

**Request Body:**

```json
{
  "name": "Marketing",
  "description": "Marketing and Communications"
}
```

### Position Management

#### Get Positions

```http
GET /positions/
```

#### Create Position

```http
POST /positions/
```

**Request Body:**

```json
{
  "name": "Senior Software Engineer",
  "description": "Senior level software development role"
}
```

### Location Management

#### Get Locations

```http
GET /locations/
```

#### Create Location

```http
POST /locations/
```

**Request Body:**

```json
{
  "name": "San Francisco Office",
  "address": "456 Tech St",
  "city": "San Francisco",
  "country": "USA"
}
```

## Health & Monitoring

### Health Check

Check API health and status.

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "redis": {
    "status": "connected",
    "rate_limiting": true
  },
  "rate_limiting": {
    "backend": "redis",
    "limit": 100,
    "window": 60
  },
  "database": {
    "status": "connected",
    "type": "sqlite"
  }
}
```

### Rate Limit Info

Get current rate limiting information.

```http
GET /rate-limit-info
```

**Response:**

```json
{
  "client_id": "rate_limit:127.0.0.1:org1",
  "rate_limit": 100,
  "window_size": 60,
  "backend": "redis",
  "redis_available": true,
  "current_requests": 5,
  "remaining_requests": 95
}
```

## Rate Limiting

### Headers

All responses include rate limiting headers:

- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Window`: Time window in seconds
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Backend`: Backend used (redis/memory)

### Rate Limit Exceeded

When rate limit is exceeded:

**Status Code:** `429 Too Many Requests`

**Headers:**

- `Retry-After`: Seconds to wait before retrying

**Response:**

```json
{
  "message": "Rate limit exceeded",
  "retry_after": 60,
  "rate_limit": 100,
  "window_size": 60,
  "backend": "redis"
}
```

## Error Codes

| Status Code | Error Type            | Description                       |
| ----------- | --------------------- | --------------------------------- |
| 400         | Bad Request           | Invalid request parameters        |
| 401         | Unauthorized          | Missing or invalid authentication |
| 403         | Forbidden             | Insufficient permissions          |
| 404         | Not Found             | Resource not found                |
| 409         | Conflict              | Resource already exists           |
| 422         | Validation Error      | Request validation failed         |
| 429         | Too Many Requests     | Rate limit exceeded               |
| 500         | Internal Server Error | Server error                      |

## Pagination

For endpoints that return lists, pagination is supported:

**Request Parameters:**

- `page`: Page number (1-based)
- `page_size`: Items per page (max 100)

**Response Format:**

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

## Filtering

### Status Filter

Filter employees by status:

```json
{
  "status": ["active", "inactive"]
}
```

### Name Search

Search by name or email (case-insensitive, partial match):

```json
{
  "name": "john"
}
```

### ID Filters

Filter by related entity IDs:

```json
{
  "department_ids": [1, 2, 3],
  "position_ids": [1, 2],
  "location_ids": [1]
}
```

## Column Selection

Specify which columns to return:

```json
{
  "columns": ["name", "email", "department", "position"]
}
```

**Available Columns:**

- `name`
- `email`
- `phone`
- `status`
- `department`
- `position`
- `location`

**Note:** Column availability depends on organization configuration.

## Multi-Tenant Isolation

### Organization Context

Each request is scoped to an organization:

1. **JWT Token**: `organization_id` claim in token
2. **Header**: `organization-id` header
3. **Default**: Falls back to "default" organization

### Data Isolation

- All data is completely isolated per organization
- Employees in `org1` cannot see employees in `org2`
- Rate limits are separate per organization
- Column configurations are per organization

## Examples

### Complete Employee Search

```bash
curl -X POST "https://api.company.com/api/v1/employees/search" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -H "organization-id: org1" \
  -d '{
    "status": ["active"],
    "department_ids": [1, 2],
    "name": "john",
    "page": 1,
    "page_size": 10,
    "columns": ["name", "email", "department", "position"]
  }'
```

### Create Employee with Full Details

```bash
curl -X POST "https://api.company.com/api/v1/employees/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -H "organization-id: org1" \
  -d '{
    "name": "Alice Johnson",
    "email": "alice.johnson@company.com",
    "phone": "+1-555-0199",
    "status": "active",
    "department_id": 1,
    "position_id": 3,
    "location_id": 2
  }'
```

### High-Performance Async Search

```bash
curl -X POST "https://api.company.com/api/v1/async/employees/search" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -H "organization-id: org1" \
  -d '{
    "page": 1,
    "page_size": 50
  }'
```
