# Stage 1: Build frontend
FROM node:18-alpine as frontend-builder

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Build backend
FROM python:3.11-slim as backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY back/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY back/ .

# Stage 3: Production image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY --from=backend /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# Copy application code
COPY --from=backend /app /app
COPY --from=frontend-builder /app/build /app/frontend/build

# Configure nginx
COPY docker/nginx.conf /etc/nginx/nginx.conf
RUN rm /etc/nginx/conf.d/default.conf

# Copy entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ports
EXPOSE 80 8080

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Install Python for backend
RUN apk add --no-cache python3 py3-pip

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy static assets from frontend build
COPY --from=frontend /app/build /usr/share/nginx/html

# Copy backend code
COPY --from=backend /app/back /app/back

# Set environment variables
ENV FLASK_APP=back/app.py
ENV FLASK_ENV=production
ENV PORT=8080

# Expose ports
EXPOSE 8080

# Start command
CMD ["nginx", "-g", "daemon off;"]
