#!/bin/sh
set -e

# Start backend in background
cd /app
uvicorn app:app --host 0.0.0.0 --port 8080 &

# Start nginx in foreground
exec nginx -g 'daemon off;'
