#
# Stage 1: Build Frontend
#
FROM node:lts-alpine AS build-frontend

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build frontend with environment args
ARG VITE_AUTH_URL
ARG VITE_AUTH_CLIENT_ID
ENV VITE_AUTH_URL=$VITE_AUTH_URL
ENV VITE_AUTH_CLIENT_ID=$VITE_AUTH_CLIENT_ID
RUN npm run build


#
# Stage 2: Production - Python Backend + Built Frontend
#
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for geospatial libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libexpat1 \
    libgdal-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY python/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python application code
COPY python/ ./

# Copy built frontend from build stage
COPY --from=build-frontend /app/frontend/dist ./static

# Set environment
ENV PYTHONUNBUFFERED=1
EXPOSE 4000

# Start the Python API server
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "4000"]
