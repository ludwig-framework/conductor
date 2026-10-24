<p align="center">
  <img src="assets/logo.png" alt="Conductor Logo" width="120"/>
</p>

<h1 align="center">Conductor</h1>
<p align="center">Production-grade AI agent orchestration for Python</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="MIT License"></a>
  <a href="#"><img src="https://img.shields.io/badge/python-3.10+-blue" alt="Python 3.10+"></a>
</p>

---

## What is Conductor?

Conductor is a framework for building, deploying, and orchestrating AI agents. It handles the hard parts: state management, tool execution, multi-agent coordination, and production deployment.

```python
from conductor import Agent, Tool, Workflow

# Define an agent with tools
research_agent = Agent(
    name="researcher",
    model="gpt-4o",
    tools=[web_search, document_reader],
    instructions="You are a research assistant."
)

# Run it
result = await research_agent.run("Latest developments in quantum computing?")
```

---

## Why Conductor?

Building AI agents that work in production is hard. You need streaming, tool calling, retries, state persistence, observability, and multi-agent coordination. Most frameworks either oversimplify or require too much boilerplate.

**Conductor's approach:**
- Minimal abstraction - Work directly with agents, tools, and workflows
- Production-first - Built-in observability, retries, and state management
- Multi-agent native - First-class support for agent coordination
- Model agnostic - OpenAI, Anthropic, local models, or any provider

---

## Installation

```bash
pip install conductor-agents
```

Or from source:
```bash
git clone https://github.com/NanaBright/conductor.git
cd conductor
pip install -e .
```

---

## Core Concepts

### Agents

Agents are the core unit. Each has a model, instructions, and optional tools.

```python
from conductor import Agent

agent = Agent(
    name="assistant",
    model="claude-3-5-sonnet",
    instructions="You are a helpful assistant.",
    temperature=0.7
)

response = await agent.run("Explain transformers in ML")
```

### Tools

Tools give agents capabilities. Sync and async supported.

```python
from conductor import Tool

@Tool(description="Search the web for information")
async def web_search(query: str) -> str:
    # Your implementation
    return results

@Tool(description="Execute Python code safely")
def run_code(code: str) -> str:
    # Sandboxed execution
    return output
```

### Workflows

Orchestrate multiple agents in sequence.

```python
from conductor import Workflow, Agent

researcher = Agent(name="researcher", model="gpt-4o", tools=[web_search])
writer = Agent(name="writer", model="claude-3-5-sonnet")

workflow = Workflow([
    ("research", researcher, "Find information about {topic}"),
    ("write", writer, "Write an article based on: {research.output}")
])

result = await workflow.run(topic="AI agents in 2026")
```

### Memory

Agents can maintain state across conversations.

```python
from conductor import Agent, Memory

agent = Agent(
    name="assistant",
    model="gpt-4o",
    memory=Memory(backend="redis", ttl=3600)
)

await agent.run("My name is Alex")
await agent.run("What's my name?")  # Remembers "Alex"
```

---

## CLI

```bash
# Create a new project
conductor new my-agent-project

# Run an agent
conductor run agent.py

# Start dev server with hot reload
conductor dev

# Deploy
conductor deploy --target kubernetes
```

---

## Multi-Agent Swarms

Build systems where agents collaborate dynamically.

```python
from conductor import Agent, Swarm

coder = Agent(name="coder", model="gpt-4o", tools=[run_code, file_write])
reviewer = Agent(name="reviewer", model="claude-3-5-sonnet")
tester = Agent(name="tester", model="gpt-4o", tools=[run_tests])

swarm = Swarm(
    agents=[coder, reviewer, tester],
    coordinator="hierarchical"  # or "round-robin", "consensus"
)

result = await swarm.run("Build a REST API for user management")
```

---

## Production Features

- **Streaming** - Real-time token streaming for all models
- **Retries** - Automatic retry with exponential backoff
- **Observability** - Built-in tracing and metrics (OpenTelemetry)
- **Cost tracking** - Token usage and cost estimation
- **Rate limiting** - Configurable per-model limits
- **Caching** - Response caching with TTL

```python
from conductor import Agent, Config

config = Config(
    retry_attempts=3,
    timeout=30,
    enable_tracing=True,
    cache_ttl=3600
)

agent = Agent(name="assistant", model="gpt-4o", config=config)
```

---

## Documentation

- [Getting Started](docs/GETTING_STARTED.md) - Installation and first agent
- [Core Concepts](docs/CONCEPTS.md) - Agents, tools, and workflows
- [API Reference](docs/API.md) - Complete API documentation
- [Deployment](docs/DEPLOYMENT.md) - Production deployment guides

---

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
git clone https://github.com/NanaBright/conductor.git
cd conductor
pip install -e ".[dev]"
pytest
```

---

## License

MIT License - see [LICENSE](LICENSE)

## Free & Open Source by Default

Conductor uses free, local models by default via [Ollama](https://ollama.com). No API keys required to get started.

```bash
ollama pull llama-3.2
```

```python
from conductor import Agent

agent = Agent(name="assistant", model="llama-3.2")
result = await agent.run("Hello!")
```
