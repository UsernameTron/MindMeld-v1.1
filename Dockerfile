FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directories for outputs
RUN mkdir -p reports logs outputs

# Health check - simple check if Python is working
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default environment settings
ENV MAX_RETRIES=3 \
    BASE_TIMEOUT=30 \
    OLLAMA_HOST="http://ollama:11434" \
    FALLBACK_MODEL="llama2"

# Expose any needed ports (for future API service)
EXPOSE 8000

# Default command - run basic help
CMD ["python", "run_agent.py", "--help"]
