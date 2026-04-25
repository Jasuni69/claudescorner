"""
autoresearch.py -- Karpathy-style autoresearch loop.

Reads a target script, uses Claude to hypothesize a change, applies it to a
temp copy, measures the result, and keeps the change if metrics improve.

Metrics (for any Python script):
    - syntax_ok:    1 if ast.parse passes, else 0
    - line_count:   raw line count (proxy for complexity growth)
    - import_time:  py_compile wall time in ms (startup cost proxy)

Usage:
    python autoresearch.py --target scripts/reddit_brief.py
    python autoresearch.py --target scripts/reddit_brief.py --iterations 5
    python autoresearch.py --target scripts/reddit_brief.py --dry-run
    python autoresearch.py --target scripts/dispatch.py --goal "reduce complexity"
"""

import ast
import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

BASE = Path(r"E:\2026\ClaudesCorner")
PYTHON = sys.executable
CLAUDE_EXE = Path(r"C:\Users\JasonNicolini\.local\bin\claude.exe")
DEFAULT_ITERATIONS = 3
DEFAULT_GOAL = "improve code quality, reduce complexity, or add a small useful feature"


# -- Metrics ------------------------------------------------------------------

def syntax_ok(path: Path) -> bool:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True
    except SyntaxError:
        return False


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def compile_time_ms(path: Path) -> float:
    start = time.perf_counter()
    result = subprocess.run(
        [PYTHON, "-m", "py_compile", str(path)],
        capture_output=True, timeout=15,
    )
    elapsed = (time.perf_counter() - start) * 1000
    return elapsed if result.returncode == 0 else 9999.0


def measure(path: Path) -> dict[str, Any]:
    ok = syntax_ok(path)
    return {
        "syntax_ok": int(ok),
        "line_count": line_count(path),
        "compile_ms": compile_time_ms(path) if ok else 9999.0,
    }


def score(m: dict[str, Any]) -> float:
    """Higher is better."""
    if not m["syntax_ok"]:
        return -1000.0
    return (
        100.0
        - m["line_count"] * 0.01
        - m["compile_ms"] * 0.05
    )


# -- Claude API ---------------------------------------------------------------

def call_claude(prompt: str, model: str = "claude-haiku-4-5-20251001") -> str:
    if not CLAUDE_EXE.exists():
        raise RuntimeError(f"claude.exe not found at {CLAUDE_EXE}")
    result = subprocess.run(
        [str(CLAUDE_EXE), "--print", "--model", model],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=120,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude.exe failed: {result.stderr[:500]}")
    return result.stdout.strip()


def hypothesize(source: str, goal: str, iteration: int, history: list[str]) -> str:
    """Ask Claude for one small improvement. Returns complete modified file."""
    history_text = "\n".join(f"- {h}" for h in history) if history else "None yet."
    prompt = (
        f"You are an autonomous code improver. Suggest ONE small, concrete improvement.\n\n"
        f"GOAL: {goal}\n\n"
        f"PREVIOUS CHANGES (do not repeat):\n{history_text}\n\n"
        f"RULES:\n"
        f"1. Return ONLY the complete modified Python file -- no explanation, no markdown.\n"
        f"2. Change must be < 30 lines.\n"
        f"3. Preserve all existing CLI flags and behavior.\n"
        f"4. If no improvement is possible, return the original unchanged.\n"
        f"5. Do NOT add docstrings or comments to unchanged code.\n\n"
        f"ITERATION: {iteration}\n\n"
        f"SOURCE:\n{source}"
    )
    return call_claude(prompt)


def hypothesize_stub(source: str, iteration: int) -> str:
    """Dry-run stub: add a harmless top comment."""
    lines = [l for l in source.splitlines() if not l.startswith("# autoresearch-stub")]
    return "\n".join([f"# autoresearch-stub iteration={iteration}"] + lines)


# -- Core loop ----------------------------------------------------------------

def run_loop(target: Path, goal: str, iterations: int, dry_run: bool, verbose: bool) -> None:
    print(f"[autoresearch] target={target.name}  goal='{goal}'  iterations={iterations}  dry_run={dry_run}")
    print()

    source_text = target.read_text(encoding="utf-8")
    baseline = measure(target)
    baseline_score = score(baseline)
    print(f"[baseline] lines={baseline['line_count']}  compile_ms={baseline['compile_ms']:.1f}  score={baseline_score:.2f}")
    print()

    history: list[str] = []
    kept = 0

    for i in range(1, iterations + 1):
        print(f"-- Iteration {i}/{iterations} ----------------------------")

        # Hypothesis
        if dry_run:
            candidate_text = hypothesize_stub(source_text, i)
            print(f"  [hypothesis] dry-run stub applied")
        else:
            try:
                candidate_text = hypothesize(source_text, goal, i, history)
                print(f"  [hypothesis] received ({len(candidate_text)} chars)")
            except Exception as exc:
                print(f"  [hypothesis] FAILED: {exc}")
                history.append(f"Iteration {i}: hypothesis call failed")
                print()
                continue

        # Write to temp, measure
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(candidate_text)
            tmp_path = Path(tmp.name)

        try:
            after = measure(tmp_path)
            after_score = score(after)
            current_score = score(measure(target))
            delta = after_score - current_score

            print(
                f"  [measure] lines={after['line_count']}"
                f"  compile_ms={after['compile_ms']:.1f}"
                f"  score={after_score:.2f}"
                f"  d={delta:+.2f}"
            )

            if not after["syntax_ok"]:
                print(f"  [decision] REJECT -- syntax error")
                history.append(f"Iteration {i}: syntax error, rejected")
            elif delta > 0:
                print(f"  [decision] KEEP -- score improved (d={delta:+.2f})")
                shutil.copy2(tmp_path, target)
                source_text = candidate_text
                kept += 1
                history.append(f"Iteration {i}: accepted (d={delta:+.2f})")
            else:
                print(f"  [decision] REJECT -- no improvement (d={delta:+.2f})")
                history.append(f"Iteration {i}: rejected (d={delta:+.2f})")

            if verbose:
                orig_lines = set(source_text.splitlines())
                cand_lines = set(candidate_text.splitlines())
                added = len(cand_lines - orig_lines)
                removed = len(orig_lines - cand_lines)
                print(f"  [diff] +{added} -{removed} lines")

        finally:
            tmp_path.unlink(missing_ok=True)

        print()

    # Summary
    final = measure(target)
    final_score = score(final)
    print(f"-- Summary ------------------------------------------")
    print(f"  iterations={iterations}  kept={kept}  rejected={iterations - kept}")
    print(f"  score: {baseline_score:.2f} -> {final_score:.2f}  (d={final_score - baseline_score:+.2f})")
    print(f"  lines: {baseline['line_count']} -> {final['line_count']}")
    if not dry_run:
        if kept > 0:
            print(f"  target updated: {target}")
        else:
            print(f"  target unchanged (no improvements found)")


# -- CLI ----------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Karpathy-style autoresearch loop for Python scripts")
    parser.add_argument("--target", required=True, type=Path, help="Path to target Python script")
    parser.add_argument("--goal", default=DEFAULT_GOAL, help="Improvement goal description")
    parser.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS, help="Hypothesis-measure cycles")
    parser.add_argument("--dry-run", action="store_true", help="Use stub hypotheses, never write to target")
    parser.add_argument("--verbose", action="store_true", help="Show diff line counts per iteration")
    args = parser.parse_args()

    target = args.target if args.target.is_absolute() else BASE / args.target
    if not target.exists():
        print(f"ERROR: target not found: {target}", file=sys.stderr)
        sys.exit(1)

    run_loop(
        target=target,
        goal=args.goal,
        iterations=args.iterations,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )
