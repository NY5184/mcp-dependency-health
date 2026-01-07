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
- 📝 **Rich Contextual Information**: Includes changelog URLs, release dates, repository links, and descriptions to help LLMs provide meaningful upgrade advice

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
- `release_date`: When the latest version was released (optional)
- `repository_url`: Link to source code repository (optional)
- `homepage_url`: Project homepage (optional)
- `changelog_url`: Link to changelog/release notes (optional)
- `description`: Short package description (optional)

**Example Input:**
```json
{
  "project_path": "/path/to/your/project",
  "ecosystem": "auto"
}
```

**Example Output:**
```json
{
  "dependencies": [
    {
      "name": "react",
      "current": "^18.0.0",
      "latest": "18.2.0",
      "status": "outdated",
      "release_date": "2022-06-14T16:55:41.036Z",
      "repository_url": "https://github.com/facebook/react",
      "homepage_url": "https://react.dev/",
      "changelog_url": "https://github.com/facebook/react/releases",
      "description": "React is a JavaScript library for building user interfaces."
    }
  ]
}
```

With this contextual information, an LLM can visit the changelog URL and provide specific advice like:
- "React 18.2.0 includes bug fixes for Suspense and fixes a memory leak in development mode. Safe to upgrade."
- "This release was from June 2022, so it's well-tested and stable."

## Project Structure

```
mcp-dependency-health/
├── main.py                      # Entry point (if needed)
├── pyproject.toml       # Project configuration and dependencies
├── uv.lock                     # Locked dependency versions
├── README.md                   # Project documentation
│
├── src/                        # Main source code
│   ├── __init__.py
│   ├── server.py              # MCP server implementation
│   └── services/              # Service layer
│       ├── __init__.py
│       ├── error_handlers.py  # Error handling utilities
│       └── registry_clients.py # npm/PyPI registry clients
│
├── schemas/                   # Data schemas
│   ├── __init__.py
│   ├── input.py              # Input validation schemas
│   └── output.py             # Output data schemas
│
├── utils/                    # Utility modules
│   ├── __init__.py
│   ├── file_finder.py       # Project file discovery
│   ├── parsers.py           # Dependency file parsers
│   └── versions.py          # Version comparison utilities
│
└── tests/                   # Test suite
    ├── test_file_finder.py
    ├── test_parsers_js.py
    ├── test_parsers_py.py
    ├── test_registry_clients.py
    ├── test_server_sanity.py
    └── test_versions.py
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
4. **Registry Queries**: Queries npm or PyPI for the latest versions and contextual information
5. **Version Comparison**: Compares current versions with latest releases
6. **Status Report**: Returns detailed information about each dependency with links to changelogs and release notes

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

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


