"""
watchdog.py — service/port monitor

Reads a YAML config, polls services (process name or TCP port) every N seconds,
logs failures and recoveries, optionally restarts via restart_cmd.

Usage:
    python watchdog.py --config watchdog.yaml [--once] [--dry-run]
"""
from __future__ import annotations

import argparse
import datetime
import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


# ── ANSI colours ─────────────────────────────────────────────────────────────
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


def _now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _log(msg: str, logfile: Path | None) -> None:
    line = f"[{_now()}] {msg}"
    print(line)
    if logfile:
        with logfile.open("a") as f:
            f.write(line + "\n")


# ── YAML fallback parser (no deps) ───────────────────────────────────────────
def _parse_yaml_fallback(text: str) -> dict[str, Any]:
    """Minimal YAML parser — handles the exact structure watchdog.yaml uses."""
    result: dict[str, Any] = {}
    services: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_services = False

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        if ":" in stripped and not line.startswith(" "):
            key, _, val = stripped.partition(":")
            val = val.strip().strip('"').strip("'")
            if key == "services":
                in_services = True
                continue
            elif key in ("interval", "logfile"):
                try:
                    result[key] = int(val) if key == "interval" else val
                except ValueError:
                    result[key] = val
            continue

        if in_services:
            if stripped.startswith("- name:"):
                if current is not None:
                    services.append(current)
                current = {"name": stripped[7:].strip().strip('"')}
            elif current is not None and ":" in stripped:
                k, _, v = stripped.partition(":")
                v = v.strip().strip('"').strip("'")
                if k.strip() == "port":
                    current["port"] = int(v) if v else None
                elif k.strip() == "process":
                    current["process"] = v
                elif k.strip() == "restart_cmd":
                    current["restart_cmd"] = v
                elif k.strip() == "enabled":
                    current["enabled"] = v.lower() != "false"

    if current is not None:
        services.append(current)

    result["services"] = services
    return result


def load_config(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text)
    return _parse_yaml_fallback(text)


# ── Checks ────────────────────────────────────────────────────────────────────
def check_port(port: int, host: str = "127.0.0.1", timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def check_process(name: str) -> bool:
    """Return True if a process matching `name` is running (Windows + Unix)."""
    try:
        if sys.platform == "win32":
            out = subprocess.check_output(
                ["tasklist", "/FI", f"IMAGENAME eq {name}", "/NH"],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            return name.lower() in out.lower()
        else:
            out = subprocess.check_output(
                ["pgrep", "-x", name], stderr=subprocess.DEVNULL, text=True
            )
            return bool(out.strip())
    except subprocess.CalledProcessError:
        return False


def restart_service(cmd: str, dry_run: bool, logfile: Path | None) -> None:
    if dry_run:
        _log(f"  [dry-run] would restart: {cmd}", logfile)
        return
    _log(f"  restarting: {cmd}", logfile)
    try:
        subprocess.Popen(cmd, shell=True)
    except Exception as exc:  # noqa: BLE001
        _log(f"  restart failed: {exc}", logfile)


# ── State tracker ─────────────────────────────────────────────────────────────
class ServiceState:
    def __init__(self, name: str) -> None:
        self.name = name
        self.alive = True  # assume up at start
        self.fail_count = 0
        self.last_restart: datetime.datetime | None = None

    def record(self, alive: bool) -> tuple[bool, bool]:
        """Return (was_alive, is_alive_now) — caller detects transitions."""
        was = self.alive
        self.alive = alive
        if not alive:
            self.fail_count += 1
        else:
            self.fail_count = 0
        return was, alive


# ── Main loop ─────────────────────────────────────────────────────────────────
def poll_once(
    services: list[dict[str, Any]],
    states: dict[str, ServiceState],
    dry_run: bool,
    logfile: Path | None,
) -> list[dict[str, Any]]:
    results = []
    for svc in services:
        if not svc.get("enabled", True):
            continue
        name: str = svc["name"]
        port: int | None = svc.get("port")
        process: str | None = svc.get("process")
        restart_cmd: str | None = svc.get("restart_cmd")

        if port is not None:
            alive = check_port(port)
            kind = f"port {port}"
        elif process:
            alive = check_process(process)
            kind = f"process {process}"
        else:
            continue

        state = states.setdefault(name, ServiceState(name))
        was, now = state.record(alive)

        status = f"{GREEN}OK{RESET}" if alive else f"{RED}DOWN{RESET}"
        results.append({"name": name, "kind": kind, "alive": alive})

        if was and not now:
            _log(f"{RED}[DOWN]{RESET}  {name} ({kind}) went down (fail #{state.fail_count})", logfile)
            if restart_cmd:
                restart_service(restart_cmd, dry_run, logfile)
        elif not was and now:
            _log(f"{GREEN}[UP]{RESET}    {name} ({kind}) recovered after {state.fail_count} checks", logfile)
        else:
            print(f"  {status}  {name} ({kind})")

    return results


def run(config_path: Path, once: bool, dry_run: bool) -> None:
    cfg = load_config(config_path)
    interval: int = cfg.get("interval", 30)
    logfile_str: str | None = cfg.get("logfile")
    logfile: Path | None = Path(logfile_str) if logfile_str else None
    services: list[dict[str, Any]] = cfg.get("services", [])

    if logfile and not logfile.is_absolute():
        logfile = config_path.parent / logfile

    enabled = [s for s in services if s.get("enabled", True)]
    _log(f"watchdog: {len(enabled)} services, interval={interval}s, dry_run={dry_run}", logfile)

    states: dict[str, ServiceState] = {}

    while True:
        print(f"\n{CYAN}--- poll {_now()} ---{RESET}")
        poll_once(services, states, dry_run, logfile)
        if once:
            break
        time.sleep(interval)


# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="Service/port watchdog")
    parser.add_argument("--config", default="watchdog.yaml", help="YAML config file")
    parser.add_argument("--once", action="store_true", help="Poll once and exit")
    parser.add_argument("--dry-run", action="store_true", help="Skip restarts")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Config not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    try:
        run(config_path, once=args.once, dry_run=args.dry_run)
    except KeyboardInterrupt:
        print("\nwatchdog stopped.")


if __name__ == "__main__":
    main()
