# MCP Dependency Health Checker

A Model Context Protocol (MCP) server that performs comprehensive health checks on project dependencies for JavaScript and Python projects.

## Features

- 🔍 **Automatic Ecosystem Detection**: Detects whether your project is JavaScript or Python
- 📦 **Package Manager Support**: 
  - JavaScript: npm-compatible (`package.json`)
  - Python: pip (`requirements.txt`)
- 🔄 **Real-time Registry Queries**: Fetches latest versions from npm and PyPI
- ⚠️ **Outdated Dependency Detection**: Compares current versions with latest releases
- 🚨 **Pre-release Detection**: Identifies pre-release versions
- 📊 **Detailed Status Reports**: Provides comprehensive information about each dependency
- 🤖 **LLM-First Design**: Clean, text-focused output designed for optimal LLM consumption
- 🚀 **Automatic Changelog Fetching**: Fetches actual release notes from GitHub releases so LLMs can analyze specific changes, bug fixes, and breaking changes without additional web requests
- 📝 **Always Actionable**: Every dependency includes meaningful changelog content - either actual release notes or clear explanations when fetching fails

## Installation

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/NY5184/mcp-dependency-health.git
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
- `changelog_content`: Always present - contains actual release notes when successfully fetched, or an explanatory message with source link if fetching failed
- `note`: Additional information (optional)
- `release_date`: When the latest version was released (optional)
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
      "changelog_content": "Release v18.2.0:\n\n## Fixes\n- Fix memory leak in development mode\n- Fix Suspense bug with nested components\n- Improve TypeScript definitions\n\n## Features\n- Add useId hook\n- Suspense improvements",
      "release_date": "2022-06-14T16:55:41.036Z",
      "description": "React is a JavaScript library for building user interfaces."
    }
  ]
}
```

**LLM-First Design:**
The output is designed for optimal LLM consumption:
- ✅ **No URL clutter** - URLs are used internally but not exposed in the output
- ✅ **Always actionable** - `changelog_content` always contains meaningful text
- ✅ **Self-contained** - LLMs can provide specific upgrade advice without additional web requests
- ✅ **Clear fallbacks** - When changelog fetching fails, the content explains what happened

**Example changelog_content values:**
- **Success**: Actual release notes from GitHub
- **Fetch failed with source**: `"Changelog available at: https://github.com/user/repo/releases\n\nThe release notes exist but could not be automatically extracted. Visit the URL above for full details."`
- **No source found**: `"Changelog could not be fetched automatically. No official changelog source was found."`

With this structure, an LLM can immediately provide specific advice like:
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
│       ├── changelog_fetcher.py # Changelog content fetching
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
5. **Changelog Fetching**: Automatically fetches release notes from GitHub releases (when available)
6. **Version Comparison**: Compares current versions with latest releases
7. **Status Report**: Returns detailed information about each dependency with actual changelog content and links

## Limitations

This tool has **limited package manager support**. It currently only supports:

### Supported Package Managers
- **JavaScript**: npm (via `package.json`)
- **Python**: pip (via `requirements.txt`)

### Unsupported Package Managers
The following package managers are **not currently supported**:
- **Python**: Poetry (`pyproject.toml`), Pipenv (`Pipfile`), Conda (`environment.yml`)
- **Rust**: Cargo (`Cargo.toml`)
- **Go**: Go modules (`go.mod`)
- **Java**: Maven (`pom.xml`), Gradle (`build.gradle`)
- **PHP**: Composer (`composer.json`)
- **.NET**: NuGet (`.csproj`, `packages.config`)
- **Ruby**: Bundler (`Gemfile`)
- **Other**: Any other package manager not listed above

When a project uses an unsupported package manager or no supported dependency file is found, the tool will return a dependency result with:
- `status`: `"unknown"`
- A clear note explaining that the project uses an unsupported dependency manager and listing the currently supported ones

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


