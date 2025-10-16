# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server for Databricks integration. The project uses Python 3.13+ and is managed with `uv` package manager.

## Development Commands

### Package Management
- Install dependencies: `uv sync`
- Add a dependency: `uv add <package>`
- Run the application: `uv run python main.py`
- Run with MCP CLI: `uv run mcp dev main.py`

### Python Environment
- Python version: 3.13+
- Package manager: uv (NOT pip or poetry)
- Always use `uv` commands for dependency management

## Architecture

### Core Dependencies
- **databricks-sdk**: Official Databricks SDK for Python API integration
- **mcp[cli]**: Model Context Protocol framework for building MCP servers
- **python-dotenv**: Environment variable management for Databricks credentials

### MCP Server Pattern
This project follows the MCP server architecture:
- Implements tools/resources that LLMs can use to interact with Databricks
- Entry point should use MCP server decorators and handlers
- Configuration typically loaded from environment variables or dotenv files

### Expected Structure
When implementing MCP server functionality:
- Define tools using MCP decorators (e.g., `@server.tool()`)
- Define resources using `@server.resource()` if needed
- Use Databricks SDK client for API interactions
- Handle authentication via environment variables (DATABRICKS_HOST, DATABRICKS_TOKEN, etc.)

## Environment Configuration

Databricks credentials should be configured via environment variables:
- `DATABRICKS_HOST`: Databricks workspace URL
- `DATABRICKS_TOKEN`: Personal access token or service principal token
- Alternative: Use `.env` file with python-dotenv for local development
