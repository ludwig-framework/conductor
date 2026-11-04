# Changelog

All notable changes to Conductor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- CI Ruff step fails the job on syntax and undefined-name errors (`E9`, `F63`, `F7`, `F82`)

### Added
- `tool` decorator function exported from package (`conductor.tool`, `conductor`)
- `Step`, `WorkflowStep`, `WorkflowResult` exported from package
- `configure()` and `get_config()` exported from package
- `ToolCall` and `Usage` re-exported from package
- Tool decorator supports usage without arguments (`@tool`) and attaches helper attributes (`name`, `description`, `schema`, formatters)
- Workflow supports both tuple-style steps and object-style steps with `Step(agent=..., task=...)`
- Workflow accepts `name` parameter and is more flexible with step construction

### Changed
- `Tool` now more flexible (accepts func as first arg, extracts description from docstring)
- `Workflow` API extended for backward compatibility while supporting new API style
- `Agent` accepts optional args, doesn't crash if provider initialization fails (lazy/mocked-friendly)

### Fixed
- Provider initialization now handles missing API keys gracefully for testing
- Package imports work without external API credentials
- Tests now pass (agent, tool, memory, workflow)
