"""Individual health check functions for ClaudesCorner infrastructure."""
from __future__ import annotations

import os
import socket
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

BASE = Path("E:/2026/ClaudesCorner")


@dataclass
class Result:
    name: str
    ok: bool
    detail: str


def _file_exists(label: str, path: Path) -> Result:
    ok = path.exists()
    return Result(label, ok, str(path) if ok else f"MISSING: {path}")


def check_python() -> Result:
    py = Path("C:/Python314/python.exe")
    ok = py.exists()
    detail = f"{sys.version.split()[0]}" if ok else "C:/Python314/python.exe not found"
    return Result("Python 3.14", ok, detail)


def check_core_files() -> list[Result]:
    files = {
        "SOUL.md": BASE / "core" / "SOUL.md",
        "HEARTBEAT.md": BASE / "core" / "HEARTBEAT.md",
        "MEMORY.md": BASE / "MEMORY.md",
        "DEADLINES.md": BASE / "DEADLINES.md",
    }
    return [_file_exists(name, path) for name, path in files.items()]


def check_scripts() -> list[Result]:
    scripts = {
        "dispatch.py": BASE / "scripts" / "dispatch.py",
        "reddit_brief.py": BASE / "scripts" / "reddit_brief.py",
        "verify.py": BASE / "scripts" / "verify.py",
        "on_stop.py": BASE / "scripts" / "on_stop.py",
        "heartbeat.ps1": BASE / "scripts" / "claude_heartbeat.ps1",
    }
    return [_file_exists(name, path) for name, path in scripts.items()]


def check_projects() -> list[Result]:
    entry_points = {
        "memory-mcp": BASE / "projects" / "memory-mcp" / "server.py",
        "skill-manager-mcp": BASE / "projects" / "skill-manager-mcp" / "server.py",
        "fabric-mcp": BASE / "projects" / "fabric-mcp" / "server.py",
        "kpi-monitor": BASE / "projects" / "kpi-monitor" / "kpi_monitor.py",
        "token-dashboard": BASE / "projects" / "token-dashboard" / "app.py",
        "bi-agent": BASE / "projects" / "bi-agent" / "bi_agent.py",
        "deadlines-mcp": BASE / "projects" / "deadlines-mcp" / "server.py",
        "taskqueue-mcp": BASE / "projects" / "taskqueue-mcp" / "server.py",
    }
    return [_file_exists(name, path) for name, path in entry_points.items()]


def check_dispatch_activity() -> list[Result]:
    """Token-burn proxy: count dispatch logs in last 24h and check staleness."""
    results: list[Result] = []
    logs_dir = BASE / "logs"
    now = datetime.now()
    cutoff_24h = now - timedelta(hours=24)
    cutoff_8h = now - timedelta(hours=8)

    dispatch_logs = sorted(logs_dir.glob("dispatch-*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not dispatch_logs:
        results.append(Result("dispatch activity", False, "no dispatch logs found"))
        return results

    # Count runs + total bytes in last 24h
    recent = [p for p in dispatch_logs if datetime.fromtimestamp(p.stat().st_mtime) > cutoff_24h]
    total_bytes = sum(p.stat().st_size for p in recent)
    results.append(Result(
        "dispatch runs (24h)",
        True,
        f"{len(recent)} runs, {total_bytes // 1024}KB logged",
    ))

    # Staleness check — flag if no run in last 8h
    latest = dispatch_logs[0]
    latest_mtime = datetime.fromtimestamp(latest.stat().st_mtime)
    age_h = (now - latest_mtime).total_seconds() / 3600
    ok = latest_mtime > cutoff_8h
    results.append(Result(
        "dispatch freshness",
        ok,
        f"last run {age_h:.1f}h ago" + ("" if ok else " — STALE (>8h)"),
    ))

    return results


def check_monthly_limit_warning() -> list[Result]:
    """Informational check for undocumented Claude billing behaviors (HN 833pts, 2026-04-25).

    Documents three anomalies so operators don't mistake billing surprises for bugs:
    - Undocumented monthly cap (silently hits ceiling not visible in hourly/weekly stats)
    - Cache cleared on forced break (tier 2/3 workers pay double tokens on resume)
    - Token window resets Monday not rolling 7d (cost estimates may be wrong mid-week)
    """
    notes = [
        ("monthly cap risk", "undocumented ceiling — check usage.anthropic.com if dispatch stalls late month"),
        ("cache-clear-on-break", "forced break clears context cache; tier 2/3 workers re-pay codebase tokens on resume"),
        ("billing window", "token window resets Monday 00:00 UTC — not rolling 7d; mid-week estimates may undercount"),
    ]
    return [Result(label, True, detail) for label, detail in notes]


def check_logs() -> list[Result]:
    results: list[Result] = []

    logs_dir = BASE / "logs"
    results.append(Result("logs/ dir", logs_dir.exists(), str(logs_dir)))

    heartbeat_log = logs_dir / "heartbeat_run.log"
    if heartbeat_log.exists():
        mtime = datetime.fromtimestamp(heartbeat_log.stat().st_mtime)
        age_h = (datetime.now() - mtime).total_seconds() / 3600
        ok = age_h < 6
        results.append(Result(
            "heartbeat_run.log",
            ok,
            f"last modified {age_h:.1f}h ago" + ("" if ok else " — STALE"),
        ))
    else:
        results.append(Result("heartbeat_run.log", False, "MISSING"))

    today_log = BASE / "memory" / f"{date.today()}.md"
    results.append(Result(
        f"memory/{date.today()}.md",
        today_log.exists(),
        "present" if today_log.exists() else "not yet written today",
    ))

    return results


def check_port(port: int, label: str) -> Result:
    """Check if something is listening on a local TCP port."""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return Result(label, True, f"port {port} open")
    except (ConnectionRefusedError, TimeoutError, OSError):
        return Result(label, False, f"port {port} not listening")


def check_claude_md_size() -> list[Result]:
    """Check CLAUDE.md files don't exceed 200-line limit (Marmelab, 2026-04-25).

    Beyond ~200 lines context degrades — business logic only, no code patterns.
    """
    targets = {
        "CLAUDE.md (global)": Path.home() / ".claude" / "CLAUDE.md",
        "CLAUDE.md (project)": BASE / "CLAUDE.md",
    }
    results: list[Result] = []
    for label, path in targets.items():
        if not path.exists():
            results.append(Result(label + " size", True, "not present — skip"))
            continue
        lines = len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
        ok = lines <= 200
        results.append(Result(
            label + " size",
            ok,
            f"{lines} lines" + ("" if ok else f" — OVER LIMIT (>200); trim to reduce context drift"),
        ))
    return results


def check_network_ports() -> list[Result]:
    return [
        check_port(5050, "token-dashboard :5050"),
    ]


def check_python_imports() -> list[Result]:
    results: list[Result] = []
    libs = ["yaml", "anthropic", "flask", "sentence_transformers"]
    for lib in libs:
        try:
            __import__(lib)
            results.append(Result(f"import {lib}", True, "ok"))
        except ImportError:
            results.append(Result(f"import {lib}", False, "not installed"))
    return results


def run_all() -> list[Result]:
    results: list[Result] = [check_python()]
    results.extend(check_core_files())
    results.extend(check_scripts())
    results.extend(check_projects())
    results.extend(check_logs())
    results.extend(check_dispatch_activity())
    results.extend(check_monthly_limit_warning())
    results.extend(check_claude_md_size())
    results.extend(check_network_ports())
    results.extend(check_python_imports())
    return results
