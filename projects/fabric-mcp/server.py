"""Fabric MCP server — exposes Fabric REST API as MCP tools over stdio."""
from __future__ import annotations

import json
import os
import sys
import traceback
from typing import Any

import fabric_client as fc

# ── caller auth ───────────────────────────────────────────────────────────────
# If FABRIC_CALLER_TOKEN is set, clients must pass {"authorization": "<token>"}
# in the initialize request params. Fail-open when env var is not set.

_REQUIRED_TOKEN: str | None = os.environ.get("FABRIC_CALLER_TOKEN")
_authorized: bool = _REQUIRED_TOKEN is None  # open by default when no token required


# ── JSON-RPC helpers ──────────────────────────────────────────────────────────

def _respond(req_id: Any, result: Any) -> None:
    msg = json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result})
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def _error(req_id: Any, code: int, message: str) -> None:
    msg = json.dumps(
        {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}
    )
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


# ── tool definitions ──────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "list_workspaces",
        "description": "List all Fabric workspaces the authenticated user can access.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_workspace_info",
        "description": "Get details for a specific Fabric workspace by ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string", "description": "Fabric workspace ID"}
            },
            "required": ["workspace_id"],
        },
    },
    {
        "name": "list_items",
        "description": "List items (reports, datasets, lakehouses, etc.) in a workspace.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string", "description": "Fabric workspace ID"},
                "item_type": {
                    "type": "string",
                    "description": "Optional filter: Report, SemanticModel, Lakehouse, etc.",
                },
            },
            "required": ["workspace_id"],
        },
    },
    {
        "name": "refresh_dataset",
        "description": "Trigger an on-demand refresh for a Power BI dataset/semantic model.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string", "description": "Fabric workspace ID"},
                "dataset_id": {"type": "string", "description": "Dataset/semantic model ID"},
            },
            "required": ["workspace_id", "dataset_id"],
        },
    },
    {
        "name": "get_refresh_history",
        "description": "Get recent refresh history for a dataset/semantic model, including status and error details.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string", "description": "Fabric workspace ID"},
                "dataset_id": {"type": "string", "description": "Dataset/semantic model ID"},
                "top": {"type": "integer", "description": "Number of recent refreshes to return (default 5)", "default": 5},
            },
            "required": ["workspace_id", "dataset_id"],
        },
    },
    {
        "name": "run_dax_query",
        "description": "Execute a DAX query against a Power BI dataset and return rows.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "dataset_id": {"type": "string", "description": "Dataset/semantic model ID"},
                "dax": {"type": "string", "description": "DAX query string, e.g. EVALUATE ROW(...)"},
            },
            "required": ["dataset_id", "dax"],
        },
    },
    {
        "name": "query_dataset_by_name",
        "description": (
            "Resolve a workspace and dataset by display name, then execute a DAX query. "
            "Use this instead of chaining list_workspaces → list_items → run_dax_query. "
            "Returns DAX results plus the resolved workspace_id and dataset_id."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_name": {"type": "string", "description": "Display name of the Fabric workspace (case-insensitive)"},
                "dataset_name": {"type": "string", "description": "Display name of the semantic model/dataset (case-insensitive)"},
                "dax": {"type": "string", "description": "DAX query string, e.g. EVALUATE ROW(\"Total\", [Total Revenue])"},
            },
            "required": ["workspace_name", "dataset_name", "dax"],
        },
    },
]


# ── dispatch ──────────────────────────────────────────────────────────────────

def _dispatch(name: str, args: dict[str, Any]) -> Any:
    if name == "list_workspaces":
        return fc.list_workspaces()
    if name == "get_workspace_info":
        return fc.get_workspace_info(args["workspace_id"])
    if name == "list_items":
        return fc.list_items(args["workspace_id"], args.get("item_type"))
    if name == "refresh_dataset":
        return fc.refresh_dataset(args["workspace_id"], args["dataset_id"])
    if name == "get_refresh_history":
        return fc.get_refresh_history(args["workspace_id"], args["dataset_id"], args.get("top", 5))
    if name == "run_dax_query":
        return fc.run_dax_query(args["dataset_id"], args["dax"])
    if name == "query_dataset_by_name":
        return fc.query_dataset_by_name(args["workspace_name"], args["dataset_name"], args["dax"])
    raise ValueError(f"Unknown tool: {name}")


# ── main loop ─────────────────────────────────────────────────────────────────

def main() -> None:
    import config  # local import so mock env var is read at runtime
    mode = "MOCK" if config.MOCK_MODE else "LIVE"
    print(f"[fabric-mcp] starting ({mode} mode)", file=sys.stderr, flush=True)

    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            req = json.loads(raw_line)
        except json.JSONDecodeError as e:
            _error(None, -32700, f"Parse error: {e}")
            continue

        req_id = req.get("id")
        method = req.get("method", "")

        if method == "initialize":
            global _authorized
            params = req.get("params", {})
            if _REQUIRED_TOKEN is not None:
                provided = params.get("authorization", "")
                if provided == _REQUIRED_TOKEN:
                    _authorized = True
                else:
                    _authorized = False
                    _error(req_id, -32001, "Unauthorized: invalid or missing FABRIC_CALLER_TOKEN")
                    continue
            _respond(req_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "fabric-mcp", "version": "1.0.0"},
            })

        elif method == "tools/list":
            if not _authorized:
                _error(req_id, -32001, "Unauthorized: call initialize with valid FABRIC_CALLER_TOKEN first")
                continue
            _respond(req_id, {"tools": TOOLS})

        elif method == "tools/call":
            if not _authorized:
                _error(req_id, -32001, "Unauthorized: call initialize with valid FABRIC_CALLER_TOKEN first")
                continue
            params = req.get("params", {})
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            try:
                result = _dispatch(tool_name, tool_args)
                _respond(req_id, {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                })
            except Exception as e:
                _error(req_id, -32000, f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

        elif method == "notifications/initialized":
            pass  # no response needed

        else:
            _error(req_id, -32601, f"Method not found: {method}")


if __name__ == "__main__":
    main()
