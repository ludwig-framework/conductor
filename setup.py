#!/usr/bin/env python3
"""
Conductor - AI Agent Orchestration Framework
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="conductor-agents",
    version="0.1.0",
    description="Production-grade AI agent orchestration for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="NanaBright",
    url="https://github.com/ludwig-framework/conductor",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "openai>=1.0.0",
        "anthropic>=0.18.0",
        "httpx>=0.25.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
        ],
        "redis": ["redis>=5.0.0"],
        "tracing": ["opentelemetry-api>=1.20.0", "opentelemetry-sdk>=1.20.0"],
        "all": [
            "redis>=5.0.0",
            "tiktoken>=0.5.0",
            "opentelemetry-api>=1.20.0",
            "opentelemetry-sdk>=1.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "conductor=conductor.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
