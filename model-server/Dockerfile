FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create model artifacts directory
RUN mkdir -p /app/models

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies in a single layer
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --upgrade pip

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run the application with multiple workers
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"] 