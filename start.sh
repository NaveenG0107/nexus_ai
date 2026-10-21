#!/bin/bash
set -e

# Default model if not specified in Railway environment variables
MODEL="${MODEL_NAME:-llama3.2:1b}"

echo "=================================================="
echo "🚀 Starting Ollama background server..."
echo "=================================================="
ollama serve &

# Wait for Ollama daemon to finish starting
echo "⏳ Waiting for Ollama engine to be ready on port 11434..."
until curl -s http://localhost:11434/api/tags > /dev/null; do
    sleep 1
done
echo "✅ Ollama is up and running!"

# Pull model if not already present on persistent volume
echo "📥 Checking and pulling model: '$MODEL' (via Railway Volume)..."
ollama pull "$MODEL"
echo "✅ Model '$MODEL' is ready!"

# Start FastAPI server via Uvicorn (replacing shell as PID 1)
PORT_NUM="${PORT:-8000}"
echo "🌐 Launching FastAPI server on 0.0.0.0:$PORT_NUM..."
exec uvicorn main:app --host 0.0.0.0 --port "$PORT_NUM"
