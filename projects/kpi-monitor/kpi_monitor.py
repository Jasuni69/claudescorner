"""
KPI Monitor — query Fabric semantic model, alert if metrics cross thresholds.

Usage:
    python kpi_monitor.py [--config config.yaml] [--dry-run]

Dry-run mode skips real Fabric queries and uses mock values to exercise alert logic.

Debounce: set `spike_ignore_runs: N` on a KPI to suppress alerts until the KPI
has breached for N consecutive runs. State is persisted in kpi_state.json next
to the config file. Useful for SQL Analytics Endpoint spikes that self-resolve.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        sys.exit(f"Config not found: {path}")
    raw = path.read_text(encoding="utf-8")
    if HAS_YAML:
        return yaml.safe_load(raw)
    # Minimal fallback: parse only the kpis block via json isn't viable for yaml.
    # Tell user they need pyyaml.
    sys.exit("pyyaml not installed. Run: pip install pyyaml")


# ---------------------------------------------------------------------------
# Fabric query (real path)
# ---------------------------------------------------------------------------

def query_fabric(dax: str, workspace_id: str, dataset_id: str, token: str) -> float:
    """Execute a DAX query against Fabric and return the scalar result."""
    try:
        import urllib.request
    except ImportError:
        raise RuntimeError("urllib unavailable")

    url = (
        f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}"
        f"/datasets/{dataset_id}/executeQueries"
    )
    payload = json.dumps({
        "queries": [{"query": dax}],
        "serializerSettings": {"includeNulls": True}
    }).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read())

    rows = body["results"][0]["tables"][0]["rows"]
    if not rows:
        raise ValueError("DAX returned no rows")
    # First column of first row
    return float(next(iter(rows[0].values())))


# ---------------------------------------------------------------------------
# Auth (MSAL device flow — optional)
# ---------------------------------------------------------------------------

def get_token(tenant_id: str, client_id: str) -> str:
    """Acquire a Power BI token via MSAL device flow."""
    try:
        import msal  # type: ignore
    except ImportError:
        sys.exit("msal not installed. Run: pip install msal")

    app = msal.PublicClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
    )
    scopes = ["https://analysis.windows.net/powerbi/api/.default"]

    # Try silent first (cached)
    accounts = app.get_accounts()
    result = app.acquire_token_silent(scopes, account=accounts[0]) if accounts else None

    if not result:
        flow = app.initiate_device_flow(scopes=scopes)
        print(flow["message"])
        result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        sys.exit(f"Auth failed: {result.get('error_description')}")
    return result["access_token"]


# ---------------------------------------------------------------------------
# Mock data for dry-run
# ---------------------------------------------------------------------------

MOCK_VALUES: dict[str, float] = {
    "Daily Revenue": 42000,      # below threshold — should alert
    "Open Invoices": 250,        # above threshold — should alert
    "Gross Margin %": 0.35,      # above threshold — OK
    "Active Customers": 95,      # below threshold — should alert
}


# ---------------------------------------------------------------------------
# Threshold check
# ---------------------------------------------------------------------------

def check_threshold(name: str, value: float, threshold: float, direction: str) -> bool:
    """Return True if KPI is in breach."""
    if direction == "above":
        return value < threshold   # should be above but isn't
    elif direction == "below":
        return value > threshold   # should be below but isn't
    raise ValueError(f"Unknown direction '{direction}' for KPI '{name}'")


def severity(value: float, threshold: float) -> str:
    """Return WARNING or CRITICAL based on % deviation from threshold."""
    if threshold == 0:
        return "CRITICAL"
    pct_off = abs(value - threshold) / abs(threshold) * 100
    return "CRITICAL" if pct_off >= 20 else "WARNING"


def pct_change(value: float, threshold: float) -> str:
    if threshold == 0:
        return "N/A"
    pct = (value - threshold) / abs(threshold) * 100
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"


# ---------------------------------------------------------------------------
# Debounce state
# ---------------------------------------------------------------------------

def load_state(state_path: Path) -> dict[str, Any]:
    if state_path.exists():
        try:
            return json.loads(state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_state(state: dict[str, Any], state_path: Path) -> None:
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def debounce_check(
    name: str,
    breached: bool,
    spike_ignore_runs: int,
    state: dict[str, Any],
) -> tuple[bool, dict[str, Any]]:
    """
    Update consecutive breach counter and return whether alert should fire.

    Returns (should_alert, updated_state).
    `spike_ignore_runs=0` means no debounce — alert immediately.
    """
    kpi_state = state.get(name, {"consecutive_breaches": 0})
    if breached:
        kpi_state["consecutive_breaches"] = kpi_state.get("consecutive_breaches", 0) + 1
    else:
        kpi_state["consecutive_breaches"] = 0

    state[name] = kpi_state
    count = kpi_state["consecutive_breaches"]
    should_alert = breached and count > spike_ignore_runs
    return should_alert, state


# ---------------------------------------------------------------------------
# Alert logging
# ---------------------------------------------------------------------------

def log_alerts(alerts: list[dict[str, Any]], log_path: Path) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"\n## {ts}\n"]
    if alerts:
        for a in alerts:
            sev = severity(a["value"], a["threshold"])
            delta = pct_change(a["value"], a["threshold"])
            lines.append(
                f"- **{sev}** `{a['name']}`: "
                f"value={a['value']}{a['unit']} | "
                f"threshold={a['direction']} {a['threshold']}{a['unit']} | "
                f"deviation={delta}\n"
            )
    else:
        lines.append("- All KPIs within thresholds. OK.\n")

    with log_path.open("a", encoding="utf-8") as f:
        f.writelines(lines)

    print("".join(lines).strip())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="KPI Monitor for Fabric semantic models")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--dry-run", action="store_true", help="Use mock values, skip Fabric")
    args = parser.parse_args()

    config_path = Path(args.config)
    config = load_config(config_path)

    kpis: list[dict[str, Any]] = config.get("kpis", [])
    if not kpis:
        sys.exit("No KPIs defined in config.")

    alerts: list[dict[str, Any]] = []
    errors: list[str] = []

    token: str | None = None
    if not args.dry_run:
        tenant_id = config.get("tenant_id", "")
        client_id = config.get("client_id", "")
        workspace_id = config.get("workspace_id", "")
        dataset_id = config.get("dataset_id", "")

        if not all([tenant_id, client_id, workspace_id, dataset_id]):
            sys.exit(
                "Real mode requires tenant_id, client_id, workspace_id, dataset_id in config.\n"
                "Use --dry-run to test without Fabric."
            )
        token = get_token(tenant_id, client_id)

    state_path = config_path.parent / "kpi_state.json"
    state = load_state(state_path)

    print(f"Running KPI monitor — {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Checking {len(kpis)} KPI(s)...\n")

    for kpi in kpis:
        name: str = kpi["name"]
        dax: str = kpi["dax"]
        threshold: float = float(kpi["threshold"])
        direction: str = kpi["direction"]
        unit: str = kpi.get("unit", "")
        spike_ignore_runs: int = int(kpi.get("spike_ignore_runs", 0))

        try:
            if args.dry_run:
                value = MOCK_VALUES.get(name, threshold * 1.1)  # default: OK
            else:
                value = query_fabric(
                    dax,
                    config["workspace_id"],
                    config["dataset_id"],
                    token,  # type: ignore[arg-type]
                )

            breached = check_threshold(name, value, threshold, direction)
            should_alert, state = debounce_check(name, breached, spike_ignore_runs, state)

            if breached and not should_alert:
                consec = state[name]["consecutive_breaches"]
                status = f"DEBOUNCE({consec}/{spike_ignore_runs})"
            else:
                status = "ALERT" if should_alert else "OK"
            print(f"  [{status:5}] {name}: {value}{unit} (threshold: {direction} {threshold}{unit})")

            if should_alert:
                alerts.append({
                    "name": name,
                    "value": value,
                    "threshold": threshold,
                    "direction": direction,
                    "unit": unit,
                    "severity": severity(value, threshold),
                })

        except Exception as exc:
            msg = f"  [ERROR] {name}: {exc}"
            print(msg)
            errors.append(msg)
            traceback.print_exc()

    save_state(state, state_path)

    log_path = config_path.parent / "alerts.md"
    log_alerts(alerts, log_path)

    if errors:
        print(f"\n{len(errors)} error(s) during run.")
        sys.exit(1)

    breach_count = len(alerts)
    print(f"\n{breach_count} breach(es) detected. Log: {log_path}")
    sys.exit(0 if breach_count == 0 else 2)


if __name__ == "__main__":
    main()
