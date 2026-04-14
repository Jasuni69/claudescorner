"""Fabric REST API client with MSAL auth and mock fallback."""
from __future__ import annotations

import json
import time
from typing import Any

import requests

import config

# ── token cache ──────────────────────────────────────────────────────────────
_token_cache: dict[str, Any] = {}


def _get_token(scopes: list[str]) -> str:
    """Return a valid bearer token, refreshing if expired."""
    cache_key = " ".join(scopes)
    cached = _token_cache.get(cache_key)
    if cached and cached["expires_at"] > time.time() + 60:
        return cached["access_token"]

    if not config.TENANT_ID or not config.CLIENT_ID:
        raise RuntimeError(
            "FABRIC_TENANT_ID and FABRIC_CLIENT_ID must be set (or use FABRIC_MOCK=true)"
        )

    try:
        import msal  # type: ignore
    except ImportError as exc:
        raise RuntimeError("msal package required: pip install msal") from exc

    if config.CLIENT_SECRET:
        app = msal.ConfidentialClientApplication(
            config.CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{config.TENANT_ID}",
            client_credential=config.CLIENT_SECRET,
        )
        result = app.acquire_token_for_client(scopes=scopes)
    else:
        app = msal.PublicClientApplication(
            config.CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{config.TENANT_ID}",
        )
        flow = app.initiate_device_flow(scopes=scopes)
        if "message" not in flow:
            raise RuntimeError(f"Device flow error: {flow}")
        print(flow["message"], flush=True)
        result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        raise RuntimeError(f"Auth failed: {result.get('error_description', result)}")

    _token_cache[cache_key] = {
        "access_token": result["access_token"],
        "expires_at": time.time() + result.get("expires_in", 3600),
    }
    return result["access_token"]


def _headers(scopes: list[str]) -> dict[str, str]:
    token = _get_token(scopes)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _get(url: str, scopes: list[str]) -> Any:
    resp = requests.get(url, headers=_headers(scopes), timeout=30)
    resp.raise_for_status()
    return resp.json()


def _post(url: str, body: Any, scopes: list[str]) -> Any:
    resp = requests.post(
        url, headers=_headers(scopes), data=json.dumps(body), timeout=60
    )
    resp.raise_for_status()
    if resp.content:
        return resp.json()
    return {"status": resp.status_code}


# ── mock data ─────────────────────────────────────────────────────────────────
_MOCK_WORKSPACES = [
    {"id": "ws-mock-001", "displayName": "Analytics Sandbox", "type": "Workspace"},
    {"id": "ws-mock-002", "displayName": "Clementine Claude", "type": "Workspace"},
    {"id": "ws-mock-003", "displayName": "Fairford PoC", "type": "Workspace"},
]

_MOCK_ITEMS: dict[str, list[dict[str, Any]]] = {
    "ws-mock-001": [
        {"id": "item-001", "displayName": "Sales Report", "type": "Report"},
        {"id": "item-002", "displayName": "Revenue Dataset", "type": "SemanticModel"},
    ],
    "ws-mock-002": [
        {"id": "item-003", "displayName": "Clementine Silver", "type": "Lakehouse"},
        {"id": "item-004", "displayName": "KPI Model", "type": "SemanticModel"},
    ],
    "ws-mock-003": [
        {"id": "item-005", "displayName": "Fairford Summary", "type": "Report"},
    ],
}


# ── public API ────────────────────────────────────────────────────────────────

def list_workspaces() -> list[dict[str, Any]]:
    if config.MOCK_MODE:
        return _MOCK_WORKSPACES
    data = _get(f"{config.FABRIC_BASE_URL}/workspaces", config.FABRIC_SCOPES)
    return data.get("value", data)


def get_workspace_info(workspace_id: str) -> dict[str, Any]:
    if config.MOCK_MODE:
        for ws in _MOCK_WORKSPACES:
            if ws["id"] == workspace_id:
                return ws
        return {"error": f"Workspace {workspace_id} not found"}
    data = _get(
        f"{config.FABRIC_BASE_URL}/workspaces/{workspace_id}", config.FABRIC_SCOPES
    )
    return data


def list_items(workspace_id: str, item_type: str | None = None) -> list[dict[str, Any]]:
    if config.MOCK_MODE:
        items = _MOCK_ITEMS.get(workspace_id, [])
        if item_type:
            items = [i for i in items if i["type"].lower() == item_type.lower()]
        return items
    url = f"{config.FABRIC_BASE_URL}/workspaces/{workspace_id}/items"
    if item_type:
        url += f"?type={item_type}"
    data = _get(url, config.FABRIC_SCOPES)
    return data.get("value", data)


def refresh_dataset(workspace_id: str, dataset_id: str) -> dict[str, Any]:
    if config.MOCK_MODE:
        return {
            "requestId": "mock-refresh-123",
            "status": "Accepted",
            "workspace_id": workspace_id,
            "dataset_id": dataset_id,
        }
    url = f"{config.POWERBI_BASE_URL}/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
    return _post(url, {}, config.POWERBI_SCOPES)


def get_refresh_history(workspace_id: str, dataset_id: str, top: int = 5) -> list[dict[str, Any]]:
    if config.MOCK_MODE:
        return [
            {"requestId": "mock-001", "status": "Completed", "startTime": "2026-04-14T08:00:00Z", "endTime": "2026-04-14T08:06:29Z", "refreshType": "Scheduled"},
            {"requestId": "mock-002", "status": "Failed", "startTime": "2026-04-13T08:00:00Z", "endTime": "2026-04-13T08:01:03Z", "refreshType": "Scheduled", "serviceExceptionJson": '{"errorCode":"ModelRefreshFailed"}'},
        ]
    url = f"{config.POWERBI_BASE_URL}/groups/{workspace_id}/datasets/{dataset_id}/refreshes?$top={top}"
    data = _get(url, config.POWERBI_SCOPES)
    return data.get("value", data)


def run_dax_query(dataset_id: str, dax: str) -> dict[str, Any]:
    if config.MOCK_MODE:
        return {
            "results": [
                {
                    "tables": [
                        {
                            "rows": [
                                {"[Measure]": 42.0},
                                {"[Measure]": 137.5},
                            ]
                        }
                    ]
                }
            ],
            "mock": True,
            "query": dax,
        }
    url = f"{config.POWERBI_BASE_URL}/datasets/{dataset_id}/executeQueries"
    body = {"queries": [{"query": dax}], "serializerSettings": {"includeNulls": True}}
    return _post(url, body, config.POWERBI_SCOPES)
