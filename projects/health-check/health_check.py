"""ClaudesCorner infrastructure health checker.

Entry point: python health_check.py [--json] [--no-color]
Exit codes: 0 = all OK, 1 = one or more failures
"""
from __future__ import annotations

import argparse
import json
import sys
from checks import Result, run_all

# ANSI codes — disabled when --no-color or not a TTY
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

_USE_COLOR = True


def colorize(text: str, color: str) -> str:
    if not _USE_COLOR:
        return text
    return f"{color}{text}{RESET}"


def render_table(results: list[Result]) -> str:
    name_w = max(len(r.name) for r in results) + 2
    detail_w = max(len(r.detail) for r in results) + 2

    header = (
        f"{'Component':<{name_w}} {'Status':<8} {'Detail'}"
    )
    sep = "-" * (name_w + 8 + detail_w + 4)
    lines = [
        colorize(header, BOLD),
        sep,
    ]

    for r in results:
        status = colorize("  OK  ", GREEN) if r.ok else colorize(" FAIL ", RED)
        name = f"{r.name:<{name_w}}"
        lines.append(f"{name} [{status}] {r.detail}")

    pass_count = sum(1 for r in results if r.ok)
    fail_count = len(results) - pass_count
    summary_color = GREEN if fail_count == 0 else RED
    summary = colorize(
        f"\n{pass_count}/{len(results)} checks passed", summary_color
    )
    lines.append(sep)
    lines.append(summary)
    return "\n".join(lines)


def render_json(results: list[Result]) -> str:
    return json.dumps(
        [{"name": r.name, "ok": r.ok, "detail": r.detail} for r in results],
        indent=2,
    )


def main() -> int:
    global _USE_COLOR

    parser = argparse.ArgumentParser(description="ClaudesCorner health check")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of table")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color")
    parser.add_argument("--fail-only", action="store_true", help="Show only failing checks")
    args = parser.parse_args()

    if args.no_color or not sys.stdout.isatty():
        _USE_COLOR = False

    results = run_all()

    if args.fail_only:
        results = [r for r in results if not r.ok]

    if args.json:
        print(render_json(results))
    else:
        print(render_table(results))

    all_ok = all(r.ok for r in results)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
