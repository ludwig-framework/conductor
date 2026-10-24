"""
Config - Global and per-agent configuration
"""

from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    """
    Configuration for Conductor agents.
    
    Args:
        default_model: Default model for agents
        retry_attempts: Number of retry attempts
        retry_delay: Delay between retries in seconds
        timeout: Request timeout in seconds
        enable_tracing: Enable OpenTelemetry tracing
        enable_caching: Enable response caching
        cache_ttl: Cache time-to-live in seconds
        enable_metrics: Enable Prometheus metrics
        metrics_port: Port for metrics server
        log_level: Logging level
    """
    
    default_model: str = "llama-3.2"  # Free local model by default (Ollama)
    retry_attempts: int = 3
    retry_delay: float = 1.0
    timeout: int = 60
    enable_tracing: bool = False
    tracing_url: Optional[str] = None
    enable_caching: bool = False
    cache_ttl: int = 3600
    enable_metrics: bool = False
    metrics_port: int = 9090
    log_level: str = "INFO"
    
    # Rate limiting
    rate_limit: Optional[int] = None  # Requests per minute
    rate_limit_tokens: Optional[int] = None  # Tokens per minute
    
    # Cost tracking
    enable_cost_tracking: bool = False
    cost_limit: Optional[float] = None  # USD limit


# Global configuration instance
_global_config: Optional[Config] = None


def configure(config: Config) -> None:
    """Set global configuration."""
    global _global_config
    _global_config = config


def get_config() -> Config:
    """Get global configuration."""
    global _global_config
    if _global_config is None:
        _global_config = Config()
    return _global_config
