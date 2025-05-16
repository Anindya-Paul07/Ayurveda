# Stage 1: Build frontend
FROM node:18-alpine as frontend

WORKDIR /app

# Copy built frontend files (built locally)
COPY frontend/build ./build

# Stage 2: Build backend
FROM python:3.11-slim-buster as backend

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY back/requirements.txt .

# Install backend dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY back/ back/

# Stage 3: Production image
FROM nginx:alpine

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
