"""
verify.py — System health check. Hard facts only, no inference.
Exits 0 if all checks pass, 1 if any fail.
"""

import subprocess
import json
import os
import sys
from datetime import datetime, date
from pathlib import Path

BASE = Path(r"E:\2026\ClaudesCorner")
CLAUDE_EXE = Path(r"C:\Users\JasonNicolini\.local\bin\claude.exe")
TODAY = date.today().isoformat()

CHECKS = []

def check(name: str, status: str, detail: str, ok: bool):
    icon = "OK" if ok else "FAIL"
    CHECKS.append({"name": name, "status": icon, "detail": detail, "ok": ok})

# --- Auth ---
try:
    result = subprocess.run(
        [str(CLAUDE_EXE), "auth", "status"],
        capture_output=True, text=True, timeout=10
    )
    data = json.loads(result.stdout)
    logged_in = data.get("loggedIn", False)
    method = data.get("authMethod", "unknown")
    check("auth", "ok" if logged_in else "fail", f"loggedIn={logged_in} method={method}", logged_in)
except Exception as e:
    check("auth", "fail", f"ERROR: {e}", False)

# --- Scheduled task ---
try:
    result = subprocess.run(
        ["cmd", "/c", "schtasks /query /tn ClaudeHeartbeat /fo LIST"],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode == 0:
        lines = result.stdout.strip().splitlines()
        info = {l.split(":")[0].strip(): ":".join(l.split(":")[1:]).strip()
                for l in lines if ":" in l}
        status_val = info.get("Status", "unknown")
        next_run = info.get("Next Run Time", "unknown")
        ok = "ready" in status_val.lower() or "running" in status_val.lower()
        check("scheduled_task", status_val, f"Next run: {next_run}", ok)
    else:
        check("scheduled_task", "MISSING", "schtasks returned non-zero — task not registered", False)
except Exception as e:
    check("scheduled_task", "ERROR", str(e), False)

# --- Heartbeat log ---
hb_log = BASE / "logs" / "heartbeat_run.log"
try:
    if hb_log.exists():
        lines = hb_log.read_text(encoding="utf-8", errors="replace").strip().splitlines()
        last = next((l for l in reversed(lines) if l.strip()), "empty")
        # Find last timestamp
        last_ts = next((l for l in reversed(lines) if l.startswith("[")), None)
        age_str = "unknown"
        ok = True
        if last_ts:
            try:
                ts = datetime.strptime(last_ts[1:17], "%Y-%m-%d %H:%M")
                age_hours = (datetime.now() - ts).total_seconds() / 3600
                age_str = f"{age_hours:.1f}h ago"
                ok = age_hours < 25  # should run at least daily
            except Exception:
                pass
        check("heartbeat_log", age_str, last.strip()[:120], ok)
    else:
        check("heartbeat_log", "MISSING", str(hb_log), False)
except Exception as e:
    check("heartbeat_log", "ERROR", str(e), False)

# --- Memory freshness ---
mem_file = BASE / "memory" / f"{TODAY}.md"
if mem_file.exists():
    mtime = datetime.fromtimestamp(mem_file.stat().st_mtime)
    age_h = (datetime.now() - mtime).total_seconds() / 3600
    check("memory_today", f"exists ({age_h:.1f}h old)", str(mem_file), age_h < 24)
else:
    check("memory_today", "MISSING", f"No file at memory/{TODAY}.md", False)

# --- HEARTBEAT pending tasks ---
hb_md = BASE / "core" / "HEARTBEAT.md"
try:
    content = hb_md.read_text(encoding="utf-8")
    pending = [l.strip() for l in content.splitlines() if l.strip().startswith("- [ ]")]
    check("pending_tasks", f"{len(pending)} pending", "\n  ".join(pending) if pending else "none", True)
except Exception as e:
    check("pending_tasks", "ERROR", str(e), False)

# --- Output ---
all_ok = all(c["ok"] for c in CHECKS)
print(f"\n=== SYSTEM HEALTH — {TODAY} ===\n")
for c in CHECKS:
    icon = "OK" if c["ok"] else "!!"
    print(f"  {icon} {c['name']:<20} {c['status']:<20} {c['detail']}")

print(f"\n{'ALL OK' if all_ok else 'ISSUES FOUND'}")
sys.exit(0 if all_ok else 1)
