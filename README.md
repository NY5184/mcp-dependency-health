# MCP Dependency Health Checker

A Model Context Protocol (MCP) server that performs comprehensive health checks on project dependencies for JavaScript and Python projects.

## Features

- 🔍 **Automatic Ecosystem Detection**: Detects whether your project is JavaScript or Python
- 📦 **Multi-Package Manager Support**: 
  - JavaScript: `package.json` (npm/yarn/pnpm)
  - Python: `requirements.txt`
- 🔄 **Real-time Registry Queries**: Fetches latest versions from npm and PyPI
- ⚠️ **Outdated Dependency Detection**: Compares current versions with latest releases
- 🚨 **Pre-release Detection**: Identifies pre-release versions
- 📊 **Detailed Status Reports**: Provides comprehensive information about each dependency

## Installation

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd mcp-dependency-health
```

2. Install dependencies:
```bash
uv sync
```

## Usage

### Running the MCP Server

Start the server in development mode:

```bash
uv run mcp dev src/server.py
```

### Using with MCP Clients

Configure your MCP client (like Claude Desktop) to connect to this server:

```json
{
  "mcpServers": {
    "dependency-health": {
      "command": "uv",
      "args": ["run", "src/server.py"],
      "cwd": "/path/to/mcp-dependency-health"
    }
  }
}
```

## Available Tools

### `dependency_health_check`

Performs a comprehensive health check on project dependencies.

**Input:**
- `project_path` (string): Path to the project directory
- `ecosystem` (string, optional): `"auto"`, `"javascript"`, or `"python"` (defaults to `"auto"`)

**Output:**
Returns a list of dependencies with:
- `name`: Package name
- `current`: Currently specified version
- `latest`: Latest version available in registry
- `status`: `"up-to-date"`, `"outdated"`, or `"unknown"`
- `note`: Additional information (optional)

**Example:**
```json
{
  "project_path": "/path/to/your/project",
  "ecosystem": "auto"
}
```

## Project Structure

```

## Development

### Running Tests

```bash
uv run pytest
```

### Code Structure

- **FastMCP Framework**: Uses FastMCP for easy MCP server creation
- **Async Operations**: Leverages `httpx` for efficient async HTTP requests
- **Type Safety**: Full type hints with Pydantic models
- **Version Parsing**: Uses `packaging` library for semantic version comparison

## Dependencies

- `fastmcp` or `mcp>=1.25.0`: MCP server framework
- `httpx>=0.28.1`: Async HTTP client
- `pydantic>=2.12.5`: Data validation
- `packaging>=25.0`: Version parsing and comparison

## How It Works

1. **File Discovery**: Scans the project directory for `package.json` or `requirements.txt`
2. **Ecosystem Detection**: Automatically determines if it's a JavaScript or Python project
3. **Dependency Parsing**: Extracts package names and version specifications
4. **Registry Queries**: Queries npm or PyPI for the latest versions
5. **Version Comparison**: Compares current versions with latest releases
6. **Status Report**: Returns detailed information about each dependency

## Troubleshooting

### "Failed to canonicalize script path"

If you encounter this error:
1. Ensure you're in the project directory
2. Recreate the virtual environment: 
   ```bash
   uv sync
   ```
3. Try running directly: `uv run python src/server.py`

### Import Errors

If you see `ModuleNotFoundError`:
- Ensure all dependencies are installed: `uv sync`
- Check that you're using the correct virtual environment

## License

[Your License Here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

