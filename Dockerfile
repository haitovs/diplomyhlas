## ----- Stage 1: Build React frontend -----
FROM node:20-alpine AS frontend-build
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

## ----- Stage 2: Production image -----
FROM python:3.11-slim

WORKDIR /app

# System deps for scapy / lightgbm
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgomp1 curl && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt ./requirements.txt
COPY backend/requirements.txt ./requirements-backend.txt
RUN pip install --no-cache-dir -r requirements.txt -r requirements-backend.txt

# Application code
COPY src/ ./src/
COPY backend/ ./backend/
COPY models/ ./models/
COPY data/samples/ ./data/samples/
COPY config.yaml .

# Built frontend static files
COPY --from=frontend-build /build/dist ./frontend/dist

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl --fail http://localhost:8000/api/health || exit 1

CMD ["python", "-m", "uvicorn", "backend.main:app", \
     "--host", "0.0.0.0", "--port", "8000"]
