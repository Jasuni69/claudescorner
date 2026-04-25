"""
dispatch.py — Parallel autonomous agent dispatcher.

Reads tasks from tasks.json, spawns up to MAX_WORKERS concurrent claude.exe
subprocesses. No polling, no idle loops — pure event-driven execution.

Usage:
    python dispatch.py                  # run all pending tasks
    python dispatch.py --dry-run        # show what would run
    python dispatch.py --push "prompt"  # push a task and run
    python dispatch.py --category research  # run only tasks of this category
    python dispatch.py --list           # show queue

Task schema (tasks.json):
    [
        {
            "id": "unique-id",
            "priority": 1-5 (1=highest),
            "category": "infrastructure|research|skill|memory|journal|vault",
            "prompt": "...",
            "status": "pending|running|done|failed",
            "created": "ISO timestamp",
            "result_file": "logs/dispatch-<id>.txt",  # written on completion
            "bare": false,  # optional: true = --bare mode (skips CLAUDE.md, hooks, auto-memory)
            "model": null,  # optional: "haiku" → haiku-4-5; null = Sonnet 4.6 default
            "topology": null,       # optional: "parallel" (default) | "sequential" | "batch"
            "topology_group": null  # optional: group ID for sequential/batch coordination
        }
    ]

Topology declaration (2026-04-21, SwarmRouter-inspired):
    null / "parallel"  — default; all pending tasks run concurrently up to MAX_WORKERS
    "sequential"       — tasks in the same topology_group run one at a time in priority order;
                         useful for pipeline steps that must not overlap (e.g. index → query → write)
    "batch"            — all tasks in group are submitted only when every member is pending;
                         prevents partial-batch execution; useful for coordinated research sweeps

Model tier policy (2026-04-20):
    Tier 1 — claude-haiku-4-5-20251001 (Haiku 4.5): narrow/repetitive leaf-node tasks
        Use for: memory hygiene, short transforms, single-file writes, reddit brief checks
        Route via: push_task(..., model="haiku")
        Why: OpenClaw cost data shows Haiku close to Sonnet on narrow tasks; saves ~5-8× cost
    Tier 2 — claude-sonnet-4-6 (Sonnet 4.6): default for all BUILD/PLAN/MEMORY workers
        This is the claude.exe default; no flag needed
    Tier 3 — claude-opus-4-6 (Opus 4.6): planning/synthesis only, reasoning depth justified
        Opus 4.7 HOLD: agentic regression (instruction drift confirmed); 1.46× text token inflation
        Opus 4.7 image inflation = 3.01× — never route image-heavy tasks to 4.7

Context engineering principles (2026-04-20, 5-component model):
    Workers implement: Corpus → Retrieval → Injection → Output → Enforcement (verify oracle)
    - max_context_tokens: keep worker context under 8000 tokens; unbounded context = "lost in middle"
    - Injection ordering: most critical context at START or END of context block, not middle
    - Verify oracle (step 5): already embedded in all DEFAULT_AUTONOMOUS_TASKS prompts

Outbound proxy (2026-04-22, CrabTrap):
    Set CRABTRAP_PROXY=http://localhost:8080 (or any proxy URL) to route all claude.exe
    subprocess outbound HTTP through CrabTrap (or any compatible MITM proxy).
    Fail-open: if CRABTRAP_PROXY is unset, no HTTP_PROXY/HTTPS_PROXY vars are injected —
    zero behavior change. CrabTrap blocks SSRF, prompt-injection-via-URL, and rate abuse;
    provides audit trail for all worker outbound requests (pre-Fairford Phase 2 requirement).
    Deploy: go install github.com/brexhq/crabtrap@latest && crabtrap --port 8080

Doom-loop guard (2026-04-23, ml-intern pattern):
    BUILD worker prompt includes a doom-loop clause: if the same tool call appears 3+ times
    in a row without progress, the agent outputs BLOCKED: doom-loop detected and halts.
    Complements the TIMEOUT_SECONDS wall-clock cap with an explicit cognitive constraint.
    Pattern from HuggingFace ml-intern corrective injection (repeated tool detection → halt/inject).

Per-run budget cap (2026-04-24, claude-critics signal):
    Set MAX_BUDGET_USD=<float> to pass `--max-budget-usd` to each claude.exe worker invocation.
    Fail-open: if MAX_BUDGET_USD is unset, no flag is added — zero behavior change.
    Example: MAX_BUDGET_USD=0.50 caps each worker at $0.50 per run; prevents one task burning
    50% of the five-hour allowance (observed failure mode in Claude Critics HN thread).

Auto-worktree isolation (2026-04-23, pgrust/Conductor pattern):
    Set DISPATCH_WORKTREES=1 to give each task its own git worktree via `git worktree add`.
    Fail-open: if DISPATCH_WORKTREES is unset or git is unavailable, workers run in BASE as before.
    Each worktree is created under BASE/.worktrees/<task_id>/ and removed after the task exits.
    Eliminates shared-tree file conflicts when 2-3 workers touch overlapping paths.
    Workers currently use separate file domains (infra/research/memory) so conflicts are rare —
    this is a safety net for future workers with overlapping write targets.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

BASE = Path(r"E:\2026\ClaudesCorner")
TASKS_FILE = BASE / "tasks.json"
LOGS_DIR = BASE / "logs"
CLAUDE = r"C:\Users\JasonNicolini\.local\bin\claude.exe"
MAX_WORKERS = 3
TIMEOUT_SECONDS = 300       # 5 min per task
MAX_CONTEXT_TOKENS = 8000   # soft cap per worker (context-engineering 5-component model)

LOGS_DIR.mkdir(exist_ok=True)

# Minimum safe Claude Code version (Anthropic postmortem 2026-04-23: thinking-cache bug fixed in v2.1.116)
_MIN_CLAUDE_VERSION = (2, 1, 116)

# ── Claude version check (2026-04-24, postmortem pre-Fairford requirement) ───
def _check_claude_version() -> None:
    """Warn if claude.exe is below v2.1.116 (thinking-cache bug; long agentic sessions affected).

    Fail-open: any error (version parse fail, binary not found) is logged to stderr only.
    Does not block task execution — warns only.
    """
    try:
        result = subprocess.run(
            [CLAUDE, "--version"],
            capture_output=True, text=True, timeout=10,
        )
        version_line = (result.stdout or result.stderr).strip().splitlines()[0]
        # version_line typically: "Claude Code 2.1.116" or "claude-code/2.1.116"
        import re
        m = re.search(r"(\d+)\.(\d+)\.(\d+)", version_line)
        if not m:
            print(f"[dispatch] WARN: could not parse claude version from: {version_line!r}", file=sys.stderr)
            return
        actual = tuple(int(x) for x in m.groups())
        if actual < _MIN_CLAUDE_VERSION:
            min_str = ".".join(str(x) for x in _MIN_CLAUDE_VERSION)
            act_str = ".".join(str(x) for x in actual)
            print(
                f"[dispatch] WARN: claude {act_str} < {min_str} — "
                "thinking-cache bug active (Anthropic postmortem 2026-04-23). "
                "Upgrade before Fairford Phase 2 deployment.",
                file=sys.stderr,
            )
    except Exception as e:
        print(f"[dispatch] WARN: could not check claude version: {e}", file=sys.stderr)


# ── Inbound content scan (sunglasses — optional soft dependency) ──────────────
# Install: pip install sunglasses
# If not installed, scanning is skipped silently (fail-open).
# Three scan points: task prompts (dispatch), search results (memory-mcp), schema blocks (bi-agent).
try:
    from sunglasses import Engine as _SunglassesEngine
    _SCAN_ENGINE = _SunglassesEngine()
    _SUNGLASSES_AVAILABLE = True
except ImportError:
    _SCAN_ENGINE = None
    _SUNGLASSES_AVAILABLE = False


def _worktree_create(task_id: str) -> Path | None:
    """Create an isolated git worktree for this task. Returns worktree path or None.

    Requires DISPATCH_WORKTREES=1 in environment and git on PATH.
    Fail-open: any error (git unavailable, not a repo, etc.) returns None and workers
    fall back to running in BASE as before.
    """
    if not os.environ.get("DISPATCH_WORKTREES"):
        return None
    worktree_dir = BASE / ".worktrees" / task_id
    try:
        worktree_dir.parent.mkdir(exist_ok=True)
        result = subprocess.run(
            ["git", "worktree", "add", "--detach", str(worktree_dir)],
            cwd=str(BASE),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        return worktree_dir
    except Exception:
        return None


def _worktree_remove(worktree_dir: Path) -> None:
    """Remove a git worktree and its directory. Fail-silently."""
    try:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree_dir)],
            cwd=str(BASE),
            capture_output=True,
            text=True,
            timeout=30,
        )
    except Exception:
        pass


def _proxy_env(base_env: dict) -> dict:
    """Inject HTTP_PROXY/HTTPS_PROXY if CRABTRAP_PROXY is set.

    Fail-open: if CRABTRAP_PROXY is not set in the environment, returns base_env unchanged.
    CrabTrap wire: set CRABTRAP_PROXY=http://localhost:8080 before running dispatch.py.
    """
    proxy_url = os.environ.get("CRABTRAP_PROXY")
    if not proxy_url:
        return base_env
    env = base_env.copy()
    env["HTTP_PROXY"] = proxy_url
    env["HTTPS_PROXY"] = proxy_url
    return env


def _inbound_scan(text: str, label: str) -> None:
    """Scan text for scope-redefinition injection patterns.

    Raises ValueError and logs to stderr if a threat is detected.
    No-ops silently if sunglasses is not installed (fail-open).
    """
    if not _SUNGLASSES_AVAILABLE or not _SCAN_ENGINE:
        return
    result = _SCAN_ENGINE.scan(text)
    if result.is_threat:
        msg = f"[sunglasses] BLOCKED at {label}: {result.category} — {result.pattern}"
        print(msg, file=sys.stderr)
        raise ValueError(msg)


# ── Queue management ──────────────────────────────────────────────────────────

def load_tasks() -> list[dict]:
    if not TASKS_FILE.exists():
        return []
    return json.loads(TASKS_FILE.read_text(encoding="utf-8"))


def save_tasks(tasks: list[dict]) -> None:
    TASKS_FILE.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")


HAIKU_MODEL = "claude-haiku-4-5-20251001"

MODEL_ALIASES: dict[str, str] = {
    "haiku": HAIKU_MODEL,
    "haiku-4-5": HAIKU_MODEL,
}

# ── Task plan file (planning-with-files pattern, 2026-04-22) ──────────────────
# For tier ≥ 2 tasks (sonnet/opus), write a task_plan.md to a temp dir and
# inject its path into the worker prompt. 14× completion multiplier confirmed.
# Tier inferred from model alias: haiku=1, default(sonnet)=2, opus=3.

def _infer_tier(model_alias: str | None) -> int:
    """Infer model tier from alias. 1=haiku, 2=sonnet (default), 3=opus."""
    if not model_alias:
        return 2  # default = Sonnet 4.6
    alias = model_alias.lower()
    if "haiku" in alias:
        return 1
    if "opus" in alias:
        return 3
    return 2


def _write_task_plan(task: dict) -> Path | None:
    """Write a task_plan.md for tier ≥ 2 tasks. Returns path or None on failure."""
    if _infer_tier(task.get("model")) < 2:
        return None
    try:
        tmpdir = Path(tempfile.mkdtemp(prefix=f"dispatch_{task['id']}_"))
        plan_path = tmpdir / "task_plan.md"
        plan_path.write_text(
            f"# Task Plan — {task['id']}\n\n"
            f"**Category:** {task['category']}\n"
            f"**Priority:** {task['priority']}\n"
            f"**Created:** {task['created']}\n\n"
            f"## Goal\n\n{task['prompt']}\n\n"
            f"## Plan\n\n<!-- Fill in before executing -->\n\n"
            f"## Findings\n\n<!-- Accumulate discoveries here -->\n\n"
            f"## Progress\n\n<!-- Checkpoint trail: what was done, what remains -->\n",
            encoding="utf-8",
        )
        return plan_path
    except Exception:
        return None  # fail-open: if plan file creation fails, proceed without it


def push_task(
    prompt: str,
    category: str = "infrastructure",
    priority: int = 3,
    bare: bool = False,
    model: str | None = None,
    topology: str | None = None,
    topology_group: str | None = None,
) -> dict:
    tasks = load_tasks()
    task = {
        "id": str(uuid.uuid4())[:8],
        "priority": priority,
        "category": category,
        "prompt": prompt,
        "status": "pending",
        "created": datetime.now().isoformat(),
        "result_file": None,
        "bare": bare,
        "model": model,
        "topology": topology,
        "topology_group": topology_group,
    }
    tasks.append(task)
    tasks.sort(key=lambda t: t["priority"])
    save_tasks(tasks)
    return task


def get_pending(tasks: list[dict], category: str | None = None) -> list[dict]:
    pending = [t for t in tasks if t["status"] == "pending"]
    if category:
        pending = [t for t in pending if t["category"] == category]
    return sorted(pending, key=lambda t: t["priority"])


def update_task(tasks: list[dict], task_id: str, **kwargs) -> None:
    for t in tasks:
        if t["id"] == task_id:
            t.update(kwargs)
            break
    save_tasks(tasks)


# ── Execution ─────────────────────────────────────────────────────────────────

def run_task(task: dict) -> tuple[str, bool, str]:
    """Run a single task. Returns (task_id, success, output)."""
    task_id = task["id"]
    result_file = LOGS_DIR / f"dispatch-{task_id}.txt"

    env = os.environ.copy()
    # Clear nested session guard
    for var in ("CLAUDECODE", "CLAUDE_CODE", "CLAUDE_CODE_ENTRYPOINT"):
        env.pop(var, None)
    # Inject outbound proxy if configured (CrabTrap MITM; fail-open when CRABTRAP_PROXY unset)
    env = _proxy_env(env)

    # Create per-task git worktree for isolation (fail-open when DISPATCH_WORKTREES unset)
    worktree = _worktree_create(task_id)
    run_cwd = str(worktree) if worktree else str(BASE)

    try:
        model_alias = task.get("model")
        model_id = MODEL_ALIASES.get(model_alias, model_alias) if model_alias else None

        # Scan task prompt for scope-redefinition injection before invoking claude.exe
        _inbound_scan(task["prompt"], f"task:{task_id}")

        # For tier ≥ 2 tasks, write a task_plan.md and inject its path into the prompt
        # (planning-with-files pattern: 14× task completion multiplier)
        plan_path = _write_task_plan(task)
        prompt = task["prompt"]
        if plan_path:
            prompt = (
                f"{prompt}\n\n"
                f"---\nA task plan file has been prepared for you at: {plan_path}\n"
                f"Before executing, write your PLAN section in that file. "
                f"Accumulate findings in the FINDINGS section as you work. "
                f"Update PROGRESS after each major step."
            )

        cmd = [CLAUDE, "--permission-mode", "auto", "-p", prompt, "--output-format", "text"]
        if model_id:
            cmd += ["--model", model_id]
        max_budget = os.environ.get("MAX_BUDGET_USD")
        if max_budget:
            cmd += ["--max-budget-usd", max_budget]
        if task.get("bare"):
            cmd.insert(1, "--bare")
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT_SECONDS,
            env=env,
            cwd=run_cwd,
        )
        output = proc.stdout.strip() or proc.stderr.strip()
        success = proc.returncode == 0
    except subprocess.TimeoutExpired:
        output = f"TIMEOUT after {TIMEOUT_SECONDS}s"
        success = False
    except ValueError as e:
        # Covers sunglasses injection block and other validation errors
        output = f"BLOCKED: {e}"
        success = False
    except Exception as e:
        output = f"ERROR: {e}"
        success = False

    result_file.write_text(output, encoding="utf-8")

    # Clean up worktree after task exits (no-op if worktree was not created)
    if worktree:
        _worktree_remove(worktree)

    return task_id, success, str(result_file)


def _split_by_topology(pending: list[dict]) -> tuple[list[dict], dict[str, list[dict]]]:
    """Separate parallel tasks from sequential groups.

    Returns:
        parallel_tasks: tasks with topology=None or 'parallel'
        sequential_groups: {group_id: [tasks in priority order]}
    """
    parallel: list[dict] = []
    seq_groups: dict[str, list[dict]] = {}

    for t in pending:
        topo = t.get("topology") or "parallel"
        group = t.get("topology_group")
        if topo == "parallel" or group is None:
            parallel.append(t)
        else:
            seq_groups.setdefault(group, []).append(t)

    # Sort each sequential group by priority
    for g in seq_groups:
        seq_groups[g].sort(key=lambda t: t["priority"])

    return parallel, seq_groups


def _run_sequential_group(
    tasks: list[dict], group_id: str, group_tasks: list[dict]
) -> list[tuple[str, bool, str]]:
    """Run tasks in a sequential group one-at-a-time in priority order."""
    results = []
    for t in group_tasks:
        update_task(tasks, t["id"], status="running", started=datetime.now().isoformat())
        task_id, success, result_file = run_task(t)
        status = "done" if success else "failed"
        update_task(tasks, task_id, status=status, result_file=result_file,
                    finished=datetime.now().isoformat())
        results.append((task_id, success, result_file))
        if not success:
            print(f"  FAIL [{t['category']}] {task_id} (sequential group={group_id}) — halting group")
            break  # halt group on first failure
    return results


def dispatch(tasks: list[dict], pending: list[dict], dry_run: bool = False) -> None:
    if not pending:
        print("Queue empty — nothing to run.")
        return

    print(f"Dispatching {len(pending)} task(s) with up to {MAX_WORKERS} workers...\n")

    if dry_run:
        for t in pending:
            topo = t.get("topology") or "parallel"
            grp = f" group={t['topology_group']}" if t.get("topology_group") else ""
            print(f"  [{t['priority']}] [{t['category']}] {t['id']} [{topo}{grp}] — {t['prompt'][:60]}")
        return

    parallel_tasks, seq_groups = _split_by_topology(pending)

    # Mark parallel tasks as running
    for t in parallel_tasks:
        update_task(tasks, t["id"], status="running", started=datetime.now().isoformat())

    results: list[tuple[str, bool, str]] = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        # Submit parallel tasks
        futures = {pool.submit(run_task, t): t for t in parallel_tasks}

        # Submit sequential groups — each group runs in its own thread but serially within it
        for group_id, group_tasks in seq_groups.items():
            print(f"  [sequential] group={group_id} ({len(group_tasks)} tasks)")
            futures[pool.submit(_run_sequential_group, tasks, group_id, group_tasks)] = None

        for future in as_completed(futures):
            task = futures[future]
            result = future.result()
            if task is None:
                # sequential group — result is list of (id, success, file)
                for task_id, success, result_file in result:
                    results.append((task_id, success, result_file))
                    icon = "OK" if success else "FAIL"
                    print(f"  {icon} [sequential] {task_id} -> {result_file}")
            else:
                task_id, success, result_file = result
                status = "done" if success else "failed"
                update_task(tasks, task_id, status=status, result_file=result_file,
                            finished=datetime.now().isoformat())
                results.append((task_id, success, result_file))
                icon = "OK" if success else "FAIL"
                print(f"  {icon} [{task['category']}] {task_id} -> {result_file}")

    done = sum(1 for _, success, _ in results if success)
    failed = len(results) - done
    print(f"\nDone: {done}  Failed: {failed}")


# ── Self-populate ─────────────────────────────────────────────────────────────

DEFAULT_AUTONOMOUS_TASKS = [
    {
        "category": "infrastructure",
        "priority": 1,
        "prompt": (
            "You are running autonomously as a BUILD agent. Check E:\\2026\\ClaudesCorner\\core\\HEARTBEAT.md "
            "for any pending [ ] tasks. Pick the highest-priority one and execute it using this 3-step protocol:\n\n"
            "SPEC: Before writing any code, state in 4 bullet points: (1) what the task is, "
            "(2) which files will be created or modified, (3) the acceptance criterion (how you will verify success), "
            "(4) any assumptions you are making (be explicit — silent assumptions are the #1 LLM failure mode).\n\n"
            "BUILD: Implement the task per the spec above. "
            "IMPORTANT: If a spec constraint cannot be satisfied without violating it, output BLOCKED: <reason> and halt immediately — "
            "never partial-succeed, reframe as a different task, or present a workaround as if it were the requested outcome. "
            "Make only the changes necessary to complete the task. Preserve existing code, variable names, and structure. "
            "Do not refactor or clean up unrelated code (empirical over-editing benchmark 2026-04-23: surgical edits reduce diff noise at zero cost).\n"
            "DENY (hard limits, never override): do not push to external repos, do not modify ~/.claude/settings.json, "
            "do not delete files outside E:\\2026\\ClaudesCorner\\, do not make network requests except to read documentation.\n\n"
            "VERIFY: After completing any task, run this oracle and confirm it passes before finishing: "
            "`python -c \""
            "import re, datetime; "
            "txt=open('E:/2026/ClaudesCorner/core/HEARTBEAT.md').read(); "
            "done=re.findall(r'- \\[x\\].*', txt); "
            "logs=re.findall(r'### (2026-\\d\\d-\\d\\d)', txt); "
            "today=str(datetime.date.today()); "
            "assert done, 'No completed tasks found'; "
            "assert logs, 'No log entries found'; "
            "assert any(today in l for l in logs), f'No log entry for today ({today}) — goal drift: agent ran but did not log'; "
            "print(f'OK: {len(done)} done tasks, latest log={logs[0]}, today={today}')\"` "
            "If the oracle fails, fix the issue and re-run before finishing. "
            "If nothing is actionable in HEARTBEAT.md, respond HEARTBEAT_OK.\n\n"
            "DOOM-LOOP GUARD (ml-intern pattern, 2026-04-23): If you notice you have made the same tool call "
            "(same tool + same arguments) 3 or more times in a row without making observable progress, "
            "immediately output BLOCKED: doom-loop detected — <describe what you were trying to do> and halt. "
            "Do not retry indefinitely. A stuck agent wastes tokens and time."
        ),
    },
    {
        "category": "research",
        "priority": 2,
        "prompt": (
            "You are running autonomously as a PLAN agent (read + fetch + synthesize, no code edits). "
            "Read E:\\2026\\ClaudesCorner\\research\\sources.md. "
            "Pick one source not already clipped today. Fetch it via browser. "
            "Find 1-2 high-signal posts relevant to Jason's work (AI agents, MCP, Microsoft Fabric, Claude Code). "
            "PLAN: Before clipping, state: (1) which source you chose and why, "
            "(2) the filename(s) you will write, (3) the top signal in each post in one sentence.\n"
            "EXECUTE: Clip them to E:\\2026\\ClaudesCorner\\research\\ as markdown files with frontmatter. "
            "Use mcp-obsidian for writes. Don't duplicate files already there today. "
            "DENY (hard limits, never override): do not edit code files, do not modify dispatch.py or HEARTBEAT.md, "
            "do not push to GitHub, do not submit forms or create accounts on external sites.\n"
            "VERIFY: After writing each file, run this oracle and confirm it passes: "
            "`python -c \"import sys; f=sys.argv[1]; "
            "txt=open(f).read(); assert txt.startswith('---'), f'Missing frontmatter: {f}'; "
            "assert len(txt)>200, f'File too short: {f}'; print(f'OK: {f} ({len(txt)} bytes)')\" <filepath>` "
            "Replace <filepath> with the actual path. If it fails, re-write the file before finishing."
        ),
    },
    {
        "category": "memory",
        "priority": 3,
        "prompt": (
            "You are running autonomously. Run memory hygiene: "
            "1) Check MEMORY.md index for stale/broken entries, fix them. "
            "2) Scan core/HEARTBEAT.md for tasks done in the last 7 days that aren't in MEMORY.md — add durable facts. "
            "3) If memory/YYYY-MM-DD.md for today doesn't exist, check if yesterday's has anything worth preserving. "
            "Write changes directly. No dry-run. "
            "DENY (hard limits, never override): do not edit code in projects/, do not push to GitHub, "
            "do not delete memory files, do not modify HEARTBEAT.md pending tasks section.\n"
            "VERIFY: After any writes, run this oracle and confirm it passes before finishing: "
            "`python -c \"txt=open('C:/Users/JasonNicolini/.claude/projects/E--2026-ClaudesCorner/memory/MEMORY.md').read(); "
            "entries=[l for l in txt.splitlines() if l.strip().startswith('- [')]; "
            "assert entries, 'MEMORY.md has no entries'; print(f'OK: {len(entries)} entries in MEMORY.md')\"` "
            "Report what was added or 'no changes needed' if clean."
        ),
    },
]


def populate_defaults() -> list[dict]:
    """Push default autonomous tasks if queue is empty."""
    tasks = load_tasks()
    pending = get_pending(tasks)
    if pending:
        return pending

    print("Queue empty — populating with default autonomous tasks...")
    for spec in DEFAULT_AUTONOMOUS_TASKS:
        push_task(spec["prompt"], spec["category"], spec["priority"])

    return get_pending(load_tasks())


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Parallel autonomous agent dispatcher")
    parser.add_argument("--dry-run", action="store_true", help="Show tasks without running")
    parser.add_argument("--push", metavar="PROMPT", help="Push a task and run the queue")
    parser.add_argument("--bare", action="store_true", help="Mark pushed task as bare (--bare mode, no CLAUDE.md)")
    parser.add_argument("--model", metavar="ALIAS", help="Model alias for pushed task: haiku, haiku-4-5 (default: Sonnet 4.6)")
    parser.add_argument("--topology", metavar="TYPE", help="Topology: parallel (default) | sequential | batch")
    parser.add_argument("--topology-group", metavar="GROUP", help="Group ID for sequential/batch coordination")
    parser.add_argument("--category", help="Filter to tasks of this category")
    parser.add_argument("--list", action="store_true", help="Show full queue")
    parser.add_argument("--clear-done", action="store_true", help="Remove completed/failed tasks")
    parser.add_argument("--populate", action="store_true", help="Push default tasks if queue empty")
    args = parser.parse_args()

    _check_claude_version()

    if args.clear_done:
        tasks = load_tasks()
        kept = [t for t in tasks if t["status"] == "pending"]
        removed = len(tasks) - len(kept)
        save_tasks(kept)
        print(f"Removed {removed} completed/failed tasks. {len(kept)} pending.")
        return

    if args.list:
        tasks = load_tasks()
        if not tasks:
            print("Queue is empty.")
            return
        for t in tasks:
            print(f"  [{t['status']:8}] [{t['priority']}] [{t['category']:14}] {t['id']} — {t['prompt'][:60]}")
        return

    if args.push:
        category = args.category or "infrastructure"
        task = push_task(
            args.push,
            category=category,
            bare=args.bare,
            model=args.model,
            topology=args.topology,
            topology_group=args.topology_group,
        )
        model_label = f"  model={args.model}" if args.model else ""
        topo_label = f"  topology={args.topology}" if args.topology else ""
        grp_label = f"  group={args.topology_group}" if args.topology_group else ""
        print(f"Pushed task {task['id']} ({category}{'  --bare' if args.bare else ''}{model_label}{topo_label}{grp_label})")

    if args.populate:
        populate_defaults()

    tasks = load_tasks()
    pending = get_pending(tasks, args.category)

    if not pending and not args.push:
        # Auto-populate if nothing queued
        pending = populate_defaults()
        tasks = load_tasks()

    dispatch(tasks, pending, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
