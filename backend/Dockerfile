FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 biuai

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/biuai/.local/bin:$PATH"

# Switch to non-root user
USER biuai

# Copy requirements first to leverage Docker cache
COPY --chown=biuai:biuai requirements.txt .

# Install Python dependencies in a single layer
RUN pip install --no-cache-dir -r requirements.txt --default-timeout=120 -i https://pypi.org/simple && \
    pip install --no-cache-dir --upgrade pip

# Copy application
COPY --chown=biuai:biuai . .

# Create necessary directories
RUN mkdir -p logs data

# Expose port
EXPOSE 8000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 