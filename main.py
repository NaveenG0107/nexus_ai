import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import ollama

app = FastAPI(
    title="Railway LLM API (Powered by Ollama)",
    description="FastAPI service hosting an Ollama LLM on Railway Cloud",
    version="1.0.0"
)

# Enable CORS for web/frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from environment variables
MODEL_NAME = os.getenv("MODEL_NAME", "smollm2:135m-instruct-q8_0")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Initialize Ollama client
client = ollama.Client(host=OLLAMA_HOST)


class QueryRequest(BaseModel):
    query: str = Field(..., description="The user query/prompt for the LLM", example="Explain quantum computing in simple terms.")
    system_prompt: str | None = Field(default=None, description="Optional system instructions for the LLM", example="You are a helpful and concise assistant.")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="Sampling temperature between 0.0 and 1.0")


class QueryResponse(BaseModel):
    model: str
    response: str


@app.get("/")
def root():
    """Root info endpoint."""
    return {
        "service": "Railway LLM API",
        "model": MODEL_NAME,
        "status": "online",
        "docs_url": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint to verify Ollama status and downloaded models."""
    try:
        model_list = client.list()
        available_models = [m.get("name") or m.get("model") for m in model_list.get("models", [])]
        is_ready = any(MODEL_NAME in str(name) for name in available_models)
        return {
            "status": "ready" if is_ready else "downloading_model",
            "active_model": MODEL_NAME,
            "installed_models": available_models
        }
    except Exception as e:
        return {
            "status": "waiting_for_ollama",
            "error": str(e)
        }


@app.post("/generate", response_model=QueryResponse)
def generate(payload: QueryRequest):
    """Main inference endpoint. Client sends a query and receives the LLM response."""
    try:
        messages = []
        if payload.system_prompt:
            messages.append({"role": "system", "content": payload.system_prompt})

        messages.append({"role": "user", "content": payload.query})

        response = client.chat(
            model=MODEL_NAME,
            messages=messages,
            options={"temperature": payload.temperature}
        )

        reply_content = response["message"]["content"]
        return QueryResponse(model=MODEL_NAME, response=reply_content)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Inference error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    # Railway sets the $PORT environment variable dynamically
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
