# Conductor Deployment Guide

This guide covers best practices and patterns for deploying Conductor agents into production environments.

---

## 1. Environment Configuration

Store API keys and operational settings using environment variables. Never hardcode keys in source code.

```bash
# Optional provider keys (only needed if using external providers)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Local Ollama endpoint (default: http://localhost:11434)
export OLLAMA_HOST="http://localhost:11434"

# Optional Redis connection for persistent memory
export REDIS_URL="redis://localhost:6379/0"
```

---

## 2. Docker Deployment

A lightweight `Dockerfile` for running Conductor agents:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Conductor
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Run the agent worker or server
CMD ["python", "main.py"]
```

Build and run:

```bash
docker build -t conductor-app .
docker run --env-file .env conductor-app
```

---

## 3. Serving via FastAPI / REST API

Expose your Conductor agents over HTTP endpoints:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from conductor import Agent

app = FastAPI(title="Conductor Agent API")

agent = Agent(
    name="customer-support",
    model="llama-3.2",
    instructions="You are a customer support agent."
)

class QueryRequest(BaseModel):
    prompt: str

class QueryResponse(BaseModel):
    reply: str
    tokens: int

@app.post("/chat", response_model=QueryResponse)
async def chat_endpoint(req: QueryRequest):
    try:
        response = await agent.run(req.prompt)
        return QueryResponse(
            reply=response.content,
            tokens=response.usage.total_tokens
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

Run with Uvicorn:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 4. Production Resilience Best Practices

### Timeouts and Retries
Configure exponential backoff and request timeouts:

```python
from conductor import Agent, Config

resilient_config = Config(
    retry_attempts=3,
    timeout=45.0,  # seconds
    cache_ttl=1800 # 30 min response caching
)

agent = Agent(name="worker", config=resilient_config)
```

### Persistent Shared Memory
For multi-instance deployments behind a load balancer, connect persistent memory to Redis:

```python
from conductor import Agent, Memory

redis_memory = Memory(
    backend="redis",
    session_id="session-user-1234",
    ttl=86400  # 24 hours
)

agent = Agent(name="assistant", memory=redis_memory)
```
