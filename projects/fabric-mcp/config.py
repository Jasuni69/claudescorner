"""Configuration for Fabric MCP server — reads from environment variables."""
import os

TENANT_ID: str = os.environ.get("FABRIC_TENANT_ID", "")
CLIENT_ID: str = os.environ.get("FABRIC_CLIENT_ID", "")
CLIENT_SECRET: str = os.environ.get("FABRIC_CLIENT_SECRET", "")

# Fabric/Power BI REST base URLs
FABRIC_BASE_URL: str = "https://api.fabric.microsoft.com/v1"
POWERBI_BASE_URL: str = "https://api.powerbi.com/v1.0/myorg"

# Auth scopes
FABRIC_SCOPES: list[str] = ["https://api.fabric.microsoft.com/.default"]
POWERBI_SCOPES: list[str] = ["https://analysis.windows.net/powerbi/api/.default"]

# Mock mode: if True, return synthetic data without calling real APIs
MOCK_MODE: bool = os.environ.get("FABRIC_MOCK", "false").lower() == "true"
