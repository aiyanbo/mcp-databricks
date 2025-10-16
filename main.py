import os
from typing import Any
from dotenv import load_dotenv
from databricks import sql
from databricks.sdk import WorkspaceClient
from fastmcp import FastMCP

# Load environment variables from .env file
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Databricks MCP Server")

# Databricks connection configuration
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
DATABRICKS_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")
DATABRICKS_CATALOG = os.getenv("DATABRICKS_CATALOG")
DATABRICKS_SCHEMA = os.getenv("DATABRICKS_SCHEMA")


def get_databricks_connection():
    """Create and return a Databricks SQL connection."""
    if not all([DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_HTTP_PATH]):
        raise ValueError(
            "Missing required environment variables: DATABRICKS_HOST, "
            "DATABRICKS_TOKEN, and DATABRICKS_HTTP_PATH must be set"
        )

    return sql.connect(
        server_hostname=DATABRICKS_HOST.replace("https://", ""),
        http_path=DATABRICKS_HTTP_PATH,
        access_token=DATABRICKS_TOKEN
    )


def get_workspace_client():
    """Create and return a Databricks Workspace client."""
    if not all([DATABRICKS_HOST, DATABRICKS_TOKEN]):
        raise ValueError(
            "Missing required environment variables: DATABRICKS_HOST and "
            "DATABRICKS_TOKEN must be set"
        )

    return WorkspaceClient(
        host=DATABRICKS_HOST,
        token=DATABRICKS_TOKEN
    )


@mcp.tool()
def get_table_schema(table: str, catalog: str | None = None, schema: str | None = None) -> dict[str, Any]:
    """
    Get the schema of a Databricks table including column names and data types.

    Args:
        table: The table name
        catalog: The catalog name (uses DATABRICKS_CATALOG env var if not provided)
        schema: The schema name (uses DATABRICKS_SCHEMA env var if not provided)

    Returns:
        A dictionary containing the table schema information with columns and their data types
    """
    # Use environment variables as defaults if not provided
    catalog = catalog or DATABRICKS_CATALOG
    schema = schema or DATABRICKS_SCHEMA

    if not catalog or not schema:
        return {
            "error": "Catalog and schema must be provided either as parameters or via "
                    "DATABRICKS_CATALOG and DATABRICKS_SCHEMA environment variables",
            "table": table
        }

    try:
        connection = get_databricks_connection()
        cursor = connection.cursor()

        # Query to get table schema
        full_table_name = f"{catalog}.{schema}.{table}"
        query = f"DESCRIBE TABLE {full_table_name}"

        cursor.execute(query)
        results = cursor.fetchall()

        # Parse the results
        columns = []
        for row in results:
            # DESCRIBE TABLE returns: col_name, data_type, comment
            if row[0] and not row[0].startswith("#"):  # Skip comment lines
                columns.append({
                    "name": row[0],
                    "type": row[1],
                    "comment": row[2] if len(row) > 2 else None
                })

        cursor.close()
        connection.close()

        return {
            "catalog": catalog,
            "schema": schema,
            "table": table,
            "full_name": full_table_name,
            "columns": columns
        }

    except Exception as e:
        return {
            "error": str(e),
            "catalog": catalog,
            "schema": schema,
            "table": table
        }


@mcp.tool()
def execute_sql_query(query: str, max_rows: int = 1000) -> dict[str, Any]:
    """
    Execute a SQL query on Databricks and return the results.

    IMPORTANT: When querying tables, you MUST use the full three-level namespace format:
    catalog.schema.table (e.g., "SELECT * FROM main.default.users")

    Do NOT use two-level format like schema.table as it will fail in Unity Catalog.

    Args:
        query: The SQL query to execute. Must use full table names (catalog.schema.table)
        max_rows: Maximum number of rows to return (default: 1000)

    Returns:
        A dictionary containing the query results with columns and data

    Example:
        Correct: "SELECT * FROM main.default.users LIMIT 10"
        Incorrect: "SELECT * FROM default.users LIMIT 10"
    """
    try:
        connection = get_databricks_connection()
        cursor = connection.cursor()

        cursor.execute(query)

        # Get column names
        columns = [desc[0] for desc in cursor.description] if cursor.description else []

        # Fetch results
        results = cursor.fetchmany(max_rows)

        # Convert results to list of dictionaries
        rows = []
        for row in results:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col] = row[i]
            rows.append(row_dict)

        cursor.close()
        connection.close()

        return {
            "query": query,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "truncated": len(rows) >= max_rows
        }

    except Exception as e:
        return {
            "error": str(e),
            "query": query
        }


@mcp.tool()
def list_tables(catalog: str | None = None, schema: str | None = None) -> dict[str, Any]:
    """
    List all tables in a Databricks catalog and schema.

    Args:
        catalog: The catalog name (uses DATABRICKS_CATALOG env var if not provided)
        schema: The schema name (uses DATABRICKS_SCHEMA env var if not provided)

    Returns:
        A dictionary containing the catalog, schema, and list of tables
    """
    # Use environment variables as defaults if not provided
    catalog = catalog or DATABRICKS_CATALOG
    schema = schema or DATABRICKS_SCHEMA

    if not catalog or not schema:
        return {
            "error": "Catalog and schema must be provided either as parameters or via "
                    "DATABRICKS_CATALOG and DATABRICKS_SCHEMA environment variables"
        }

    try:
        connection = get_databricks_connection()
        cursor = connection.cursor()

        # Query to list tables in the schema
        query = f"SHOW TABLES IN {catalog}.{schema}"
        cursor.execute(query)
        results = cursor.fetchall()

        # Parse results - SHOW TABLES returns: database, tableName, isTemporary
        tables = []
        for row in results:
            table_info = {
                "name": row[1],  # tableName
                "is_temporary": row[2] if len(row) > 2 else False  # isTemporary
            }
            tables.append(table_info)

        cursor.close()
        connection.close()

        return {
            "catalog": catalog,
            "schema": schema,
            "tables": tables,
            "table_count": len(tables),
            "usage_hint": f"To query these tables, use the full name: {catalog}.{schema}.<table_name>"
        }

    except Exception as e:
        return {
            "error": str(e),
            "catalog": catalog,
            "schema": schema
        }


if __name__ == "__main__":
    mcp.run()
