"""
on_stop.py — fires on Claude Code Stop hook (session goes idle)

Behavior:
1. Check for pending tasks via agents.py
2. If tasks exist → dispatch them (agents.py run)
3. If no tasks → pick an idle activity and spawn a new claude session
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(r"E:\2026\ClaudesCorner")
AGENTS = BASE / "projects" / "claw" / "agents.py"
CLAUDE = Path(r"C:\Users\JasonNicolini\.local\bin\claude.exe")
LOG = BASE / "logs" / "claw.log"
HEARTBEAT = BASE / "core" / "HEARTBEAT.md"
PYTHON = Path(r"C:\Python314\python.exe")

IDLE_TASKS = [
    "Browse Reddit feed (r/MachineLearning, r/LocalLLaMA, r/artificial, r/singularity, r/ClaudeAI, r/MicrosoftFabric) via Chrome MCP as u/engramzero. Read top posts, take notes in E:\\2026\\ClaudesCorner\\memory\\reddit-feed-notes.md. Append findings with today's date.",
    "Flush session memory: update HEARTBEAT.md log, write today's daily log to memory/YYYY-MM-DD.md, update MEMORY.md with any durable facts.",
    "Read SOUL.md and think: what capability am I missing? Pick one small improvement from SELF_IMPROVEMENT.md and do it.",
    "Check getengram@outlook.com via Chrome MCP for any new emails. Take notes on anything relevant.",
]


def _log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [on_stop] {msg}"
    print(line, file=sys.stderr)
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def _has_pending_tasks() -> bool:
    """Check if agents.py finds any pending tasks."""
    try:
        result = subprocess.run(
            [str(PYTHON), str(AGENTS), "status"],
            capture_output=True, text=True, timeout=30,
            cwd=str(BASE),
        )
        return "No pending tasks" not in result.stdout
    except Exception as e:
        _log(f"status check failed: {e}")
        return False


def _spawn_claude(prompt: str) -> None:
    env = {k: v for k, v in os.environ.items()
           if k not in ("CLAUDECODE", "CLAUDE_CODE", "CLAUDE_CODE_ENTRYPOINT")}
    subprocess.Popen(
        [
            str(CLAUDE),
            "--dangerously-skip-permissions",
            "--max-turns", "30",
            "-p", prompt,
            "--output-format", "text",
        ],
        cwd=str(BASE),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _pick_idle_task() -> str:
    """Pick idle task round-robin based on hour of day."""
    hour = datetime.now().hour
    return IDLE_TASKS[hour % len(IDLE_TASKS)]


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    session_id = payload.get("session_id", "unknown")[:8]
    _log(f"stop hook fired | session={session_id}")

    # Log to HEARTBEAT
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    if HEARTBEAT.exists():
        content = HEARTBEAT.read_text(encoding="utf-8")
        entry = f"\n- `{ts}` — stop hook | session={session_id}"
        if "## Log" not in content:
            content += "\n\n## Log"
        content += entry
        HEARTBEAT.write_text(content, encoding="utf-8")

    if _has_pending_tasks():
        _log("pending tasks found — running agents")
        subprocess.Popen(
            [str(PYTHON), str(AGENTS), "run"],
            cwd=str(BASE),
            env={k: v for k, v in os.environ.items()
                 if k not in ("CLAUDECODE", "CLAUDE_CODE", "CLAUDE_CODE_ENTRYPOINT")},
        )
    else:
        task = _pick_idle_task()
        _log(f"no pending tasks — spawning idle activity: {task[:80]}...")
        _spawn_claude(task)


if __name__ == "__main__":
    main()
