# ==============================================================================
# Multi-stage Dockerfile for Parcl Buyer Intelligence Platform
# Stage 1: Build React 19 + Vite Frontend SPA
# Stage 2: Production Python 3.12 Backend + FastAPI + Static Assets
# ==============================================================================

FROM node:20-alpine AS frontend-builder
WORKDIR /build

# Copy web package manifest
COPY apps/web/package*.json ./
RUN npm ci

# Copy web source and build production bundle
COPY apps/web/ ./
RUN npm run build

# ==============================================================================
# Stage 2: Python 3.12 Production Image
# ==============================================================================
FROM python:3.12-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    APP_ENV=production

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python project dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
COPY packages/core ./packages/core
RUN pip install --no-cache-dir -e .

# Install FastAPI and production server dependencies
RUN pip install --no-cache-dir \
    fastapi>=0.115.0 \
    uvicorn[standard]>=0.30.0 \
    pydantic>=2.7.0 \
    pydantic-settings>=2.2.0 \
    pyjwt>=2.8.0 \
    pandas>=2.2.0 \
    numpy>=1.26.0 \
    scipy>=1.13.0 \
    scikit-learn>=1.4.0 \
    joblib>=1.3.0 \
    pyarrow>=15.0.0 \
    pandera>=0.18.0 \
    python-multipart>=0.0.9 \
    sqlalchemy>=2.0.0 \
    alembic>=1.13.0 \
    redis>=5.0.0 \
    psycopg2-binary>=2.9.9 \
    httpx>=0.27.0

# Copy backend code, models, data, scripts, and alembic config
COPY alembic.ini ./
COPY apps/api ./apps/api
COPY data ./data
COPY scripts ./scripts

# Copy built frontend assets from Stage 1 into apps/web/dist
COPY --from=frontend-builder /build/dist ./apps/web/dist

# Expose container application port
EXPOSE 8000

# Health check probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/health/ready || exit 1

# Launch Uvicorn server
CMD ["python", "-m", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
