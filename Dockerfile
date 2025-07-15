# =================================================================
# Stage 1: Build Stage - Cài đặt dependencies và chuẩn bị môi trường
# =================================================================
FROM python:3.11-slim as builder

# Cài đặt build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        sqlite3 \
        && rm -rf /var/lib/apt/lists/*

# Create virtual environment for better isolation
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy và install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# =================================================================
# Stage 2: Runtime Stage - Image cuối cùng chỉ chứa những gì cần thiết
# =================================================================
FROM python:3.11-slim as runtime

# Cài đặt chỉ runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        sqlite3 \
        && rm -rf /var/lib/apt/lists/*

# Copy virtual environment từ build stage
COPY --from=builder /opt/venv /opt/venv

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Create data directory for SQLite
RUN mkdir -p /app/data && \
    chown -R appuser:appuser /app

# Environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    SQLITE_DB=/app/data/employee_directory.db \
    PATH="/opt/venv/bin:$PATH"

# Initialize database as appuser
USER appuser
RUN python create_tables.py && \
    python -m app.db.init_script

# Expose port
EXPOSE 8000

# Health check using standard library urllib (no external dependencies)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
