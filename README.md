# Databricks MCP Server

A Model Context Protocol (MCP) server for Databricks integration, enabling LLMs to interact with Databricks workspaces, execute SQL queries, and inspect table schemas.

## Features

- **Table Schema Inspection**: Get detailed information about table structures including column names, data types, and comments
- **SQL Query Execution**: Execute SQL queries on Databricks and retrieve results
- **Environment-based Configuration**: Secure credential management using environment variables

## Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Databricks workspace with:
  - Workspace URL
  - Personal access token or service principal token
  - SQL Warehouse HTTP path

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mcp-databricks
```

2. Install dependencies:
```bash
uv sync
```

3. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and fill in your Databricks credentials:
```env
DATABRICKS_HOST=https://your-workspace.databricks.com
DATABRICKS_TOKEN=your-access-token
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your-warehouse-id
```

## Usage

### Running the MCP Server

The package provides an executable command `mcp-databricks` that you can run:

```bash
uv run mcp-databricks
```

Alternatively, you can run the main module directly:

```bash
uv run python main.py
```

For development with MCP CLI:

```bash
uv run mcp dev main.py
```

### Testing with MCP Inspector

The MCP Inspector is a powerful tool for testing and debugging your MCP server. It provides a web-based interface to interact with your server's tools.

To start the inspector:

```bash
npx @modelcontextprotocol/inspector uv run mcp-databricks
```

Or use the main module directly:

```bash
npx @modelcontextprotocol/inspector uv run python main.py
```

This will:
1. Start your MCP server
2. Launch the Inspector web interface (usually at http://localhost:5173)
3. Allow you to test tools interactively in your browser

**Using the Inspector:**
- View all available tools and their parameters
- Execute tools with custom inputs
- See real-time responses and results
- Debug connection and authentication issues

**Example workflow:**
1. Start the inspector with the command above
2. Open your browser to the provided URL
3. Select the `get_table_schema` tool
4. Enter parameters: `catalog="main"`, `schema="default"`, `table="your_table"`
5. Click "Run" to see the table schema response
6. Try the `execute_sql_query` tool with a simple query like `SELECT * FROM main.default.your_table LIMIT 10`

### Available Tools

#### 1. get_table_schema

Get the schema of a Databricks table including column names and data types.

**Parameters:**
- `catalog` (string): The catalog name
- `schema` (string): The schema name
- `table` (string): The table name

**Returns:**
```json
{
  "catalog": "main",
  "schema": "default",
  "table": "users",
  "full_name": "main.default.users",
  "columns": [
    {
      "name": "id",
      "type": "bigint",
      "comment": "User ID"
    },
    {
      "name": "name",
      "type": "string",
      "comment": "User name"
    }
  ]
}
```

#### 2. execute_sql_query

Execute a SQL query on Databricks and return the results.

**IMPORTANT:** When querying tables, you **MUST** use the full three-level namespace format: `catalog.schema.table` (e.g., `main.default.users`). Do **NOT** use two-level format like `schema.table` as it will fail in Unity Catalog.

**Parameters:**
- `query` (string): The SQL query to execute. Must use full table names (catalog.schema.table)
- `max_rows` (integer, optional): Maximum number of rows to return (default: 1000)

**Returns:**
```json
{
  "query": "SELECT * FROM main.default.users LIMIT 10",
  "columns": ["id", "name", "email"],
  "rows": [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
  ],
  "row_count": 2,
  "truncated": false
}
```

#### 3. list_tables

List all tables in a Databricks catalog and schema.

**Parameters:**
- `catalog` (string, optional): The catalog name (uses DATABRICKS_CATALOG env var if not provided)
- `schema` (string, optional): The schema name (uses DATABRICKS_SCHEMA env var if not provided)

**Returns:**
```json
{
  "catalog": "main",
  "schema": "default",
  "tables": [
    {"name": "users", "is_temporary": false},
    {"name": "orders", "is_temporary": false}
  ],
  "table_count": 2,
  "usage_hint": "To query these tables, use the full name: main.default.<table_name>"
}
```

## Configuration

### Environment Variables

The following environment variables are required:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABRICKS_HOST` | Databricks workspace URL | `https://your-workspace.databricks.com` |
| `DATABRICKS_TOKEN` | Personal access token or service principal token | `dapi1234567890abcdef` |
| `DATABRICKS_HTTP_PATH` | SQL Warehouse HTTP path | `/sql/1.0/warehouses/abc123def456` |

### Getting Databricks Credentials

1. **Workspace URL**: Found in your Databricks workspace URL (e.g., `https://your-workspace.databricks.com`)

2. **Access Token**:
   - Go to User Settings > Developer > Access Tokens
   - Click "Generate New Token"
   - Copy the generated token

3. **HTTP Path**:
   - Navigate to SQL Warehouses in your Databricks workspace
   - Select your warehouse
   - Go to Connection Details tab
   - Copy the HTTP Path

## Development

### Project Structure

```
mcp-databricks/
├── main.py              # MCP server implementation
├── pyproject.toml       # Project dependencies
├── .env.example         # Environment variables template
├── .env                 # Local configuration (gitignored)
└── README.md            # This file
```

### Dependencies

- **databricks-sdk**: Official Databricks SDK for Python
- **fastmcp**: FastMCP framework for building MCP servers
- **python-dotenv**: Environment variable management

### Adding New Tools

To add new tools, define them in `main.py` using the `@mcp.tool()` decorator:

```python
@mcp.tool()
def your_tool_name(param1: str, param2: int) -> dict:
    """
    Tool description here.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value
    """
    # Implementation
    return {"result": "data"}
```

## Security Notes

- Never commit your `.env` file to version control
- Use service principal tokens for production deployments
- Limit token permissions to only what's necessary
- Rotate access tokens regularly
- Use SQL Warehouse with appropriate access controls

## Troubleshooting

### Connection Issues

If you encounter connection errors:
1. Verify your `DATABRICKS_HOST` is correct and includes `https://`
2. Check that your access token is valid and not expired
3. Ensure your SQL Warehouse is running
4. Verify the HTTP path matches your SQL Warehouse

### Query Execution Errors

- **Table not found errors**: Always use the full three-level namespace `catalog.schema.table` in SQL queries
  - ✅ Correct: `SELECT * FROM main.default.users`
  - ❌ Incorrect: `SELECT * FROM default.users` or `SELECT * FROM users`
- Ensure the user/service principal has appropriate permissions on the catalogs, schemas, and tables
- Check that Unity Catalog is enabled if using three-level namespace (catalog.schema.table)
- Verify SQL syntax is compatible with Databricks SQL

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
