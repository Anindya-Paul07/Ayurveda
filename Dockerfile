# Base image
FROM python:3.11-slim-buster

WORKDIR /app

# Set environment variable for unbuffered output
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
COPY setup.py .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY service/ service/
COPY templates/ templates/

# Copy environment file
COPY .env .

# Copy the Data directory containing PDFs
COPY Data/ Data/

# Create wsgi.py file
RUN echo 'from app import app\nif __name__ == "__main__":\n    app.run()' > wsgi.py

# Non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "3", "wsgi:app"]
