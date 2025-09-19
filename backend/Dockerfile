# TrendXL 2.0 Backend - Python 3.10 Runtime
FROM python:3.10-slim-bullseye

# Set Python environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Verify Python installation
RUN python --version && pip --version

# Copy requirements and install Python dependencies
# Use absolute path when building from project root
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Create non-root user for security
RUN groupadd -r trendxl && useradd -r -g trendxl -u 1000 trendxl \
    && chown -R trendxl:trendxl /app
USER trendxl

# Expose port (Railway will override with $PORT environment variable)
EXPOSE 8000

# Health check with explicit python3 reference
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://127.0.0.1:${PORT:-8000}/health || exit 1

# Use explicit python3 command
CMD ["python3", "run_server.py"]
