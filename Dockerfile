# 1. Build Frontend
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# 2. Build Backend & Run App
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (for pylint/black/etc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY .env .

# Copy built frontend files from stage 1
COPY --from=frontend-build /app/frontend/build ./static

# Expose FastAPI port
EXPOSE 8000

# Start command: we'll use uvicorn to serve the API
# Render/Railway provide a $PORT env var, so we use it with a default of 8000
CMD uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-8000}
