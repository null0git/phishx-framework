# Multi-stage Docker build for PhishX Framework
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    pkg-config \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r phishx && useradd -r -g phishx phishx

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base as production

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data \
    /app/logs \
    /app/uploads \
    /app/instance \
    && chown -R phishx:phishx /app

# Switch to non-root user
USER phishx

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Start application
CMD ["python", "main.py"]

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy

# Copy application code
COPY . .

# Create directories and set permissions
RUN mkdir -p /app/data \
    /app/logs \
    /app/uploads \
    /app/instance \
    && chown -R phishx:phishx /app

# Switch to non-root user
USER phishx

# Expose port
EXPOSE 5000

# Start application in development mode
CMD ["python", "main.py"]
