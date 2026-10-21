FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Tell Ollama to store downloaded models in the persistent volume path
ENV OLLAMA_MODELS=/data/ollama/models
ENV OLLAMA_HOST=0.0.0.0:11434

WORKDIR /app

# Install system dependencies, curl, ca-certificates, and the Ollama engine
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && curl -fsSL https://ollama.com/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Ensure start.sh has Unix (LF) line endings and is executable
RUN sed -i 's/\r$//' start.sh && chmod +x start.sh

# Expose default port (Railway injects dynamic $PORT at runtime)
EXPOSE 8000

# Run our orchestrator startup script
CMD ["./start.sh"]
