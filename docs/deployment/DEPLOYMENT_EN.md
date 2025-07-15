# Deployment Guide

Complete guide for deploying Employee Directory API to production environments.

## 🌟 Deployment Options

- [Docker Compose](#docker-compose-deployment)
- [Kubernetes](#kubernetes-deployment)
- [Cloud Platforms](#cloud-platforms)
- [Manual Deployment](#manual-deployment)

## 🐳 Docker Compose Deployment

### Production Setup

**1. Create production docker-compose file:**

```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  redis:
    image: redis:7-alpine
    container_name: employee-directory-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    environment:
      - REDIS_PASSWORD=${REDIS_PASSWORD}
    healthcheck:
      test:
        [
          "CMD",
          "redis-cli",
          "--no-auth-warning",
          "-a",
          "${REDIS_PASSWORD}",
          "ping",
        ]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: employee-directory-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    depends_on:
      redis:
        condition: service_healthy
    environment:
      # Application
      - PROJECT_NAME=Employee Directory API
      - VERSION=1.0.0
      - SECRET_KEY=${SECRET_KEY}
      - DEFAULT_API_TOKEN=${DEFAULT_API_TOKEN}

      # Database
      - SQLITE_DB=/app/data/employee_directory.db
      - DB_HOST=${DB_HOST:-}
      - DB_NAME=${DB_NAME:-}
      - DB_USER=${DB_USER:-}
      - DB_PASSWORD=${DB_PASSWORD:-}

      # Redis
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - REDIS_RATE_LIMITING=true
      - REDIS_CONNECTION_TIMEOUT=10
      - REDIS_MAX_CONNECTIONS=50

      # Rate Limiting
      - RATE_LIMIT=500
      - RATE_LIMIT_WINDOW_SIZE=60

      # CORS
      - BACKEND_CORS_ORIGINS=["https://yourdomain.com", "https://api.yourdomain.com"]

      # Logging
      - LOG_LEVEL=INFO

    volumes:
      - app_data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    container_name: employee-directory-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - api

volumes:
  redis_data:
  app_data:
```

**2. Create production Dockerfile:**

```dockerfile
# Dockerfile.prod
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data && chown -R app:app /app

# Switch to app user
USER app

# Initialize database
RUN python create_tables.py
RUN python -m app.db.init_script

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**3. Create environment file:**

```bash
# .env.prod
SECRET_KEY=your-super-secret-production-key-change-this
DEFAULT_API_TOKEN=your-production-api-token
REDIS_PASSWORD=your-redis-password

# Database (optional PostgreSQL)
DB_HOST=your-postgres-host
DB_NAME=employee_directory_prod
DB_USER=your-db-user
DB_PASSWORD=your-db-password

# Domain
DOMAIN=yourdomain.com
```

**4. Deploy:**

```bash
# Load environment variables
set -a; source .env.prod; set +a

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

### SSL/TLS Configuration

**nginx.conf:**

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;

            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # Health check
        location /health {
            proxy_pass http://api/health;
            access_log off;
        }

        # Documentation
        location /docs {
            proxy_pass http://api/docs;
        }
    }
}
```

## ☸️ Kubernetes Deployment

### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: employee-directory-config
data:
  PROJECT_NAME: "Employee Directory API"
  VERSION: "1.0.0"
  REDIS_RATE_LIMITING: "true"
  RATE_LIMIT: "500"
  RATE_LIMIT_WINDOW_SIZE: "60"
  LOG_LEVEL: "INFO"
```

### Secret

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: employee-directory-secret
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret>
  DEFAULT_API_TOKEN: <base64-encoded-token>
  REDIS_PASSWORD: <base64-encoded-password>
  DB_PASSWORD: <base64-encoded-db-password>
```

### Redis Deployment

```yaml
# k8s/redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          ports:
            - containerPort: 6379
          env:
            - name: REDIS_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: employee-directory-secret
                  key: REDIS_PASSWORD
          command:
            [
              "redis-server",
              "--appendonly",
              "yes",
              "--requirepass",
              "$(REDIS_PASSWORD)",
            ]
          volumeMounts:
            - name: redis-data
              mountPath: /data
          livenessProbe:
            exec:
              command:
                - redis-cli
                - --no-auth-warning
                - -a
                - $(REDIS_PASSWORD)
                - ping
            initialDelaySeconds: 30
            periodSeconds: 10
      volumes:
        - name: redis-data
          persistentVolumeClaim:
            claimName: redis-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
spec:
  selector:
    app: redis
  ports:
    - port: 6379
      targetPort: 6379

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

### API Deployment

```yaml
# k8s/api.yaml
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
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: employee-directory-secret
                  key: SECRET_KEY
            - name: DEFAULT_API_TOKEN
              valueFrom:
                secretKeyRef:
                  name: employee-directory-secret
                  key: DEFAULT_API_TOKEN
            - name: REDIS_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: employee-directory-secret
                  key: REDIS_PASSWORD
            - name: REDIS_URL
              value: "redis://:$(REDIS_PASSWORD)@redis-service:6379/0"
          envFrom:
            - configMapRef:
                name: employee-directory-config
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: employee-directory-service
spec:
  selector:
    app: employee-directory-api
  ports:
    - port: 80
      targetPort: 8000
  type: LoadBalancer
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: employee-directory-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
    - hosts:
        - api.yourdomain.com
      secretName: employee-directory-tls
  rules:
    - host: api.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: employee-directory-service
                port:
                  number: 80
```

### Deploy to Kubernetes

```bash
# Apply configurations
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/api.yaml
kubectl apply -f k8s/ingress.yaml

# Check status
kubectl get pods
kubectl get services
kubectl get ingress

# Check logs
kubectl logs -l app=employee-directory-api
```

## ☁️ Cloud Platforms

### AWS ECS

**task-definition.json:**

```json
{
  "family": "employee-directory-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "employee-directory-api",
      "image": "your-account.dkr.ecr.region.amazonaws.com/employee-directory-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "REDIS_URL",
          "value": "redis://your-elasticache-endpoint:6379/0"
        },
        {
          "name": "REDIS_RATE_LIMITING",
          "value": "true"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:employee-directory-secret"
        }
      ],
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8000/health || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/employee-directory-api",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Run

```yaml
# cloudrun.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: employee-directory-api
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 100
      containers:
        - image: gcr.io/YOUR_PROJECT/employee-directory-api
          ports:
            - containerPort: 8000
          env:
            - name: REDIS_URL
              value: "redis://your-memorystore-ip:6379/0"
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  key: secret-key
                  name: employee-directory-secret
          resources:
            limits:
              cpu: "1"
              memory: "512Mi"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
```

### Azure Container Instances

```yaml
# azure-container.yaml
apiVersion: 2019-12-01
location: eastus
name: employee-directory-api
properties:
  containers:
    - name: employee-directory-api
      properties:
        image: yourregistry.azurecr.io/employee-directory-api:latest
        ports:
          - port: 8000
            protocol: TCP
        environmentVariables:
          - name: REDIS_URL
            value: your-azure-cache-endpoint
          - name: SECRET_KEY
            secureValue: your-secret-key
        resources:
          requests:
            cpu: 0.5
            memoryInGb: 1
  osType: Linux
  restartPolicy: Always
  ipAddress:
    type: Public
    ports:
      - protocol: tcp
        port: 8000
```

## 🖥️ Manual Deployment

### Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip nginx redis-server -y

# Create app user
sudo useradd --create-home --shell /bin/bash appuser
sudo usermod -aG sudo appuser

# Setup application directory
sudo mkdir -p /opt/employee-directory
sudo chown appuser:appuser /opt/employee-directory
```

### Application Setup

```bash
# Switch to app user
sudo su - appuser

# Clone and setup application
cd /opt/employee-directory
git clone <repository-url> .
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize database
python create_tables.py
python -m app.db.init_script

# Create production config
cat > .env << EOF
SECRET_KEY=your-production-secret-key
DEFAULT_API_TOKEN=your-production-token
REDIS_RATE_LIMITING=true
REDIS_URL=redis://localhost:6379/0
RATE_LIMIT=500
RATE_LIMIT_WINDOW_SIZE=60
LOG_LEVEL=INFO
EOF
```

### Systemd Service

```bash
# Create systemd service
sudo tee /etc/systemd/system/employee-directory.service << EOF
[Unit]
Description=Employee Directory API
After=network.target redis.service

[Service]
User=appuser
Group=appuser
WorkingDirectory=/opt/employee-directory
Environment=PATH=/opt/employee-directory/venv/bin
EnvironmentFile=/opt/employee-directory/.env
ExecStart=/opt/employee-directory/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable employee-directory
sudo systemctl start employee-directory
```

### Nginx Configuration

```bash
# Create nginx config
sudo tee /etc/nginx/sites-available/employee-directory << EOF
upstream api {
    server 127.0.0.1:8000;
}

# Rate limiting
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;

server {
    listen 80;
    server_name yourdomain.com;

    location / {
        limit_req zone=api burst=20 nodelay;

        proxy_pass http://api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /health {
        proxy_pass http://api/health;
        access_log off;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/employee-directory /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 📊 Monitoring & Logging

### Health Checks

```bash
# Application health
curl -f http://localhost:8000/health

# Redis health
redis-cli ping

# Rate limiting status
curl http://localhost:8000/api/v1/rate-limit-info
```

### Log Management

```bash
# Application logs (systemd)
sudo journalctl -u employee-directory -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Redis logs
sudo tail -f /var/log/redis/redis-server.log
```

### Performance Monitoring

```python
# monitoring/check_api.py
import requests
import time
import sys

def check_api_health():
    try:
        start_time = time.time()
        response = requests.get('http://localhost:8000/health', timeout=10)
        response_time = (time.time() - start_time) * 1000

        if response.status_code == 200:
            data = response.json()
            print(f"✅ API healthy - {response_time:.2f}ms")
            print(f"   Redis: {data['redis']['status']}")
            print(f"   Backend: {data['rate_limiting']['backend']}")
            return True
        else:
            print(f"❌ API unhealthy - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API check failed: {e}")
        return False

if __name__ == "__main__":
    if not check_api_health():
        sys.exit(1)
```

## 🔧 Maintenance

### Database Backup

```bash
# SQLite backup
cp employee_directory.db employee_directory_backup_$(date +%Y%m%d_%H%M%S).db

# PostgreSQL backup
pg_dump -h localhost -U username database_name > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Log Rotation

```bash
# Configure logrotate
sudo tee /etc/logrotate.d/employee-directory << EOF
/var/log/nginx/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 nginx nginx
    postrotate
        systemctl reload nginx
    endscript
}
EOF
```

### SSL Certificate Management

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### Updates

```bash
# Update application
cd /opt/employee-directory
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart employee-directory
```

## 📋 Production Checklist

### Security

- [ ] Strong SECRET_KEY in production
- [ ] Redis password configured
- [ ] SSL/TLS certificates installed
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Firewall configured

### Performance

- [ ] Redis enabled for rate limiting
- [ ] Database connection pooling configured
- [ ] Nginx proxy caching enabled
- [ ] Worker processes optimized
- [ ] Health checks configured

### Monitoring

- [ ] Log aggregation setup
- [ ] Health check monitoring
- [ ] Performance metrics collection
- [ ] Alerting configured
- [ ] Backup strategy implemented

### High Availability

- [ ] Multiple app instances
- [ ] Load balancer configured
- [ ] Database replication
- [ ] Redis clustering (if needed)
- [ ] Auto-scaling enabled

## 🚨 Troubleshooting

### Common Issues

**Application won't start:**

```bash
# Check logs
sudo journalctl -u employee-directory -n 50

# Check configuration
sudo -u appuser /opt/employee-directory/venv/bin/python -c "from app.core.config import settings; print(settings)"
```

**Redis connection issues:**

```bash
# Check Redis status
sudo systemctl status redis
redis-cli ping

# Check Redis config
sudo cat /etc/redis/redis.conf | grep bind
```

**High memory usage:**

```bash
# Check process memory
ps aux | grep python

# Monitor Redis memory
redis-cli info memory
```

**Performance issues:**

```bash
# Check worker processes
ps aux | grep uvicorn

# Monitor database
sqlite3 employee_directory.db ".tables"
```

---

**Ready for production!** 🚀

For questions or issues, check the troubleshooting section or create an issue in the repository.
