"""
pbip_diff.py — Compare two Power BI .pbip projects and summarize changes.

Usage:
    python pbip_diff.py <old_dir> <new_dir> [--output report.md]

Reports:
  - Pages added/removed/renamed
  - Visuals added/removed/moved (per page)
  - Visual type changes
  - Measure changes (if SemanticModel present)
  - Report-level settings/theme changes
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def find_report_dir(base: Path) -> Path | None:
    """Find the .Report directory under a .pbip base."""
    for child in base.iterdir():
        if child.is_dir() and child.name.endswith(".Report"):
            return child
    return None


def find_semantic_model_dir(base: Path) -> Path | None:
    for child in base.iterdir():
        if child.is_dir() and child.name.endswith(".SemanticModel"):
            return child
    return None


# ---------------------------------------------------------------------------
# Report parsing
# ---------------------------------------------------------------------------

def parse_pages(report_dir: Path) -> dict[str, dict]:
    """Return {page_id: {name, displayName, visuals: {id: visual_info}}}."""
    pages_json = read_json(report_dir / "definition" / "pages" / "pages.json")
    page_order = pages_json.get("pageOrder", []) if pages_json else []

    pages: dict[str, dict] = {}
    pages_dir = report_dir / "definition" / "pages"

    for page_id in page_order:
        page_dir = pages_dir / page_id
        page_data = read_json(page_dir / "page.json") or {}
        visuals = parse_visuals(page_dir / "visuals")
        pages[page_id] = {
            "name": page_data.get("name", page_id),
            "displayName": page_data.get("displayName", page_id),
            "visuals": visuals,
        }

    return pages


def parse_visuals(visuals_dir: Path) -> dict[str, dict]:
    """Return {visual_name: {type, position, ...}}."""
    visuals: dict[str, dict] = {}
    if not visuals_dir.exists():
        return visuals

    for entry in visuals_dir.iterdir():
        if not entry.is_dir():
            continue
        vdata = read_json(entry / "visual.json") or {}
        vis = vdata.get("visual", {})
        pos = vdata.get("position", {})
        visuals[entry.name] = {
            "type": vis.get("visualType", "unknown"),
            "x": pos.get("x", 0),
            "y": pos.get("y", 0),
            "width": pos.get("width", 0),
            "height": pos.get("height", 0),
            "title": _extract_title(vis),
        }
    return visuals


def _extract_title(vis: dict) -> str:
    """Best-effort title extraction from visual config."""
    try:
        objs = vis.get("objects", {})
        title_obj = objs.get("title", [{}])[0]
        props = title_obj.get("properties", {})
        text = props.get("text", {})
        if "expr" in text:
            return text["expr"].get("Literal", {}).get("Value", "").strip("'")
        return ""
    except (KeyError, IndexError, TypeError):
        return ""


def parse_report_settings(report_dir: Path) -> dict:
    rjson = read_json(report_dir / "definition" / "report.json") or {}
    return {
        "theme": rjson.get("themeCollection", {}),
        "settings": rjson.get("settings", {}),
    }


# ---------------------------------------------------------------------------
# SemanticModel parsing
# ---------------------------------------------------------------------------

def parse_measures(model_dir: Path | None) -> dict[str, dict]:
    """Return {table.measure_name: {expression, formatString}}."""
    if model_dir is None:
        return {}

    measures: dict[str, dict] = {}
    tables_dir = model_dir / "definition" / "tables"
    if not tables_dir.exists():
        return measures

    for tbl_dir in tables_dir.iterdir():
        if not tbl_dir.is_dir():
            continue
        measures_dir = tbl_dir / "measures"
        if not measures_dir.exists():
            continue
        for mfile in measures_dir.glob("*.measure.json"):
            mdata = read_json(mfile) or {}
            key = f"{tbl_dir.name}.{mdata.get('name', mfile.stem)}"
            measures[key] = {
                "expression": mdata.get("expression", ""),
                "formatString": mdata.get("formatString", ""),
                "description": mdata.get("description", ""),
            }
    return measures


# ---------------------------------------------------------------------------
# Diffing
# ---------------------------------------------------------------------------

def diff_pages(
    old_pages: dict[str, dict], new_pages: dict[str, dict]
) -> list[str]:
    lines: list[str] = []

    old_ids = set(old_pages)
    new_ids = set(new_pages)

    added = new_ids - old_ids
    removed = old_ids - new_ids
    common = old_ids & new_ids

    for pid in sorted(added):
        p = new_pages[pid]
        lines.append(f"+ Page added: **{p['displayName']}** (`{pid}`)")

    for pid in sorted(removed):
        p = old_pages[pid]
        lines.append(f"- Page removed: **{p['displayName']}** (`{pid}`)")

    for pid in sorted(common):
        op = old_pages[pid]
        np = new_pages[pid]
        if op["displayName"] != np["displayName"]:
            lines.append(
                f"~ Page renamed: `{op['displayName']}` → `{np['displayName']}` (`{pid}`)"
            )
        visual_diffs = diff_visuals(pid, op["displayName"], op["visuals"], np["visuals"])
        lines.extend(visual_diffs)

    return lines


def diff_visuals(
    page_id: str,
    page_name: str,
    old_vis: dict[str, dict],
    new_vis: dict[str, dict],
) -> list[str]:
    lines: list[str] = []
    prefix = f"  [{page_name}]"

    old_ids = set(old_vis)
    new_ids = set(new_vis)
    added = new_ids - old_ids
    removed = old_ids - new_ids
    common = old_ids & new_ids

    for vid in sorted(added):
        v = new_vis[vid]
        label = v["title"] or vid
        lines.append(f"{prefix} + Visual added: `{label}` (type: {v['type']})")

    for vid in sorted(removed):
        v = old_vis[vid]
        label = v["title"] or vid
        lines.append(f"{prefix} - Visual removed: `{label}` (type: {v['type']})")

    for vid in sorted(common):
        ov = old_vis[vid]
        nv = new_vis[vid]
        if ov["type"] != nv["type"]:
            label = nv["title"] or vid
            lines.append(
                f"{prefix} ~ Visual type changed: `{label}` {ov['type']} → {nv['type']}"
            )
        # Position change (threshold: >5px)
        dx = abs(nv["x"] - ov["x"])
        dy = abs(nv["y"] - ov["y"])
        dw = abs(nv["width"] - ov["width"])
        dh = abs(nv["height"] - ov["height"])
        if dx > 5 or dy > 5 or dw > 5 or dh > 5:
            label = nv["title"] or vid
            lines.append(
                f"{prefix} ~ Visual repositioned/resized: `{label}` "
                f"(Δx={dx:.0f} Δy={dy:.0f} Δw={dw:.0f} Δh={dh:.0f})"
            )

    return lines


def diff_measures(
    old_m: dict[str, dict], new_m: dict[str, dict]
) -> list[str]:
    lines: list[str] = []

    added = set(new_m) - set(old_m)
    removed = set(old_m) - set(new_m)
    common = set(old_m) & set(new_m)

    for k in sorted(added):
        lines.append(f"+ Measure added: **{k}**")

    for k in sorted(removed):
        lines.append(f"- Measure removed: **{k}**")

    for k in sorted(common):
        om = old_m[k]
        nm = new_m[k]
        if om["expression"].strip() != nm["expression"].strip():
            lines.append(f"~ Measure changed: **{k}**")
            # Show a short diff (first differing line)
            old_lines = om["expression"].strip().splitlines()
            new_lines = nm["expression"].strip().splitlines()
            if len(old_lines) <= 3 and len(new_lines) <= 3:
                lines.append(f"  Before: `{om['expression'].strip()}`")
                lines.append(f"  After:  `{nm['expression'].strip()}`")
        if om["formatString"] != nm["formatString"]:
            lines.append(
                f"~ Measure format changed: **{k}** "
                f"`{om['formatString']}` → `{nm['formatString']}`"
            )

    return lines


def diff_settings(old_s: dict, new_s: dict) -> list[str]:
    lines: list[str] = []
    if old_s.get("theme") != new_s.get("theme"):
        lines.append("~ Report theme changed")
    if old_s.get("settings") != new_s.get("settings"):
        lines.append("~ Report settings changed")
    return lines


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_diff(old_path: Path, new_path: Path) -> str:
    old_report = find_report_dir(old_path)
    new_report = find_report_dir(new_path)

    if old_report is None:
        # Maybe they passed the .Report dir directly
        if old_path.name.endswith(".Report"):
            old_report = old_path
        else:
            return f"ERROR: No .Report directory found in {old_path}"

    if new_report is None:
        if new_path.name.endswith(".Report"):
            new_report = new_path
        else:
            return f"ERROR: No .Report directory found in {new_path}"

    old_model = find_semantic_model_dir(old_path) if not old_path.name.endswith(".Report") else None
    new_model = find_semantic_model_dir(new_path) if not new_path.name.endswith(".Report") else None

    old_pages = parse_pages(old_report)
    new_pages = parse_pages(new_report)
    old_settings = parse_report_settings(old_report)
    new_settings = parse_report_settings(new_report)
    old_measures = parse_measures(old_model)
    new_measures = parse_measures(new_model)

    sections: list[str] = []

    # Header
    sections.append(f"# PBIP Diff Report")
    sections.append(f"**Old:** `{old_path}`  ")
    sections.append(f"**New:** `{new_path}`")
    sections.append("")

    # Summary counts
    page_diffs = diff_pages(old_pages, new_pages)
    measure_diffs = diff_measures(old_measures, new_measures)
    setting_diffs = diff_settings(old_settings, new_settings)

    total_changes = len(page_diffs) + len(measure_diffs) + len(setting_diffs)
    sections.append(f"**{total_changes} change(s) found** across pages, visuals, measures, and settings.")
    sections.append("")

    # Pages + visuals
    if page_diffs:
        sections.append("## Pages & Visuals")
        sections.extend(page_diffs)
        sections.append("")
    else:
        sections.append("## Pages & Visuals")
        sections.append("_No changes._")
        sections.append("")

    # Measures
    if old_measures or new_measures:
        sections.append("## Measures")
        if measure_diffs:
            sections.extend(measure_diffs)
        else:
            sections.append("_No changes._")
        sections.append("")

    # Settings
    if setting_diffs:
        sections.append("## Report Settings")
        sections.extend(setting_diffs)
        sections.append("")

    return "\n".join(sections)


def main() -> None:
    parser = argparse.ArgumentParser(description="Diff two Power BI .pbip projects")
    parser.add_argument("old", help="Old .pbip directory (or .Report dir)")
    parser.add_argument("new", help="New .pbip directory (or .Report dir)")
    parser.add_argument("--output", "-o", help="Write report to this file (default: stdout)")
    args = parser.parse_args()

    report = run_diff(Path(args.old), Path(args.new))

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
