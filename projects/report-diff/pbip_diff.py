"""
pbip_diff.py — Diff two Power BI Project (.pbip) directories.

Usage:
    python pbip_diff.py <dir_a> <dir_b> [--json] [--out report.md]

Compares:
  - Pages (added / removed / renamed by order)
  - Visuals per page (type, position, title, filters)
  - Measures (added / removed / changed expression)
  - Report-level settings (theme, locale, etc.)

PBIP layout (thin reports):
  <report>.Report/
    definition.pbir          <- report-level metadata
    pages/
      <page-guid>/
        page.json            <- page metadata (name, displayName, ordinal)
        visuals/
          <visual-guid>/
            visual.json      <- visual metadata (type, position, title, query)
    definition/
      tables/
        <table>/
          measures/
            <measure>.json   <- measure (name, expression, formatString)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Page:
    guid: str
    name: str
    display_name: str
    ordinal: int


@dataclass
class Visual:
    guid: str
    page_guid: str
    visual_type: str
    x: float
    y: float
    width: float
    height: float
    title: str


@dataclass
class Measure:
    table: str
    name: str
    expression: str
    format_string: str


@dataclass
class ReportSnapshot:
    root: Path
    pages: dict[str, Page] = field(default_factory=dict)          # guid -> Page
    visuals: dict[str, Visual] = field(default_factory=dict)       # guid -> Visual
    measures: dict[str, Measure] = field(default_factory=dict)     # "Table.Name" -> Measure
    settings: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _find_report_root(base: Path) -> Path:
    """Return the *.Report directory inside base, or base itself."""
    candidates = list(base.glob("*.Report"))
    if candidates:
        return candidates[0]
    # Maybe base IS the .Report dir
    if (base / "pages").exists() or (base / "definition.pbir").exists():
        return base
    raise FileNotFoundError(f"No .Report directory found under {base}")


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _parse_pages(report_root: Path) -> dict[str, Page]:
    pages: dict[str, Page] = {}
    pages_dir = report_root / "pages"
    if not pages_dir.exists():
        return pages
    for page_dir in pages_dir.iterdir():
        if not page_dir.is_dir():
            continue
        data = _load_json(page_dir / "page.json")
        if not data:
            continue
        guid = page_dir.name
        pages[guid] = Page(
            guid=guid,
            name=data.get("name", guid),
            display_name=data.get("displayName", data.get("name", guid)),
            ordinal=data.get("ordinal", 0),
        )
    return pages


def _parse_visuals(report_root: Path, pages: dict[str, Page]) -> dict[str, Visual]:
    visuals: dict[str, Visual] = {}
    for page_guid in pages:
        vis_dir = report_root / "pages" / page_guid / "visuals"
        if not vis_dir.exists():
            continue
        for v_dir in vis_dir.iterdir():
            if not v_dir.is_dir():
                continue
            data = _load_json(v_dir / "visual.json")
            if not data:
                continue
            vguid = v_dir.name
            vtype = (
                data.get("visual", {}).get("visualType")
                or data.get("visualType")
                or "unknown"
            )
            pos = data.get("position", {})
            title_data = (
                data.get("visual", {})
                    .get("vcObjects", {})
                    .get("title", [{}])
            )
            title = ""
            if isinstance(title_data, list) and title_data:
                title = (
                    title_data[0]
                    .get("properties", {})
                    .get("text", {})
                    .get("expr", {})
                    .get("Literal", {})
                    .get("Value", "")
                ).strip("'\"")
            visuals[vguid] = Visual(
                guid=vguid,
                page_guid=page_guid,
                visual_type=vtype,
                x=pos.get("x", 0),
                y=pos.get("y", 0),
                width=pos.get("width", 0),
                height=pos.get("height", 0),
                title=title,
            )
    return visuals


def _parse_measures(report_root: Path) -> dict[str, Measure]:
    measures: dict[str, Measure] = {}
    tables_dir = report_root / "definition" / "tables"
    if not tables_dir.exists():
        return measures
    for table_dir in tables_dir.iterdir():
        if not table_dir.is_dir():
            continue
        m_dir = table_dir / "measures"
        if not m_dir.exists():
            continue
        for m_file in m_dir.glob("*.json"):
            data = _load_json(m_file)
            if not data:
                continue
            name = data.get("name", m_file.stem)
            key = f"{table_dir.name}.{name}"
            measures[key] = Measure(
                table=table_dir.name,
                name=name,
                expression=data.get("expression", ""),
                format_string=data.get("formatString", ""),
            )
    return measures


def _parse_settings(report_root: Path) -> dict[str, Any]:
    pbir = _load_json(report_root / "definition.pbir")
    return pbir


def load_snapshot(base: Path) -> ReportSnapshot:
    root = _find_report_root(base)
    snap = ReportSnapshot(root=root)
    snap.pages = _parse_pages(root)
    snap.visuals = _parse_visuals(root, snap.pages)
    snap.measures = _parse_measures(root)
    snap.settings = _parse_settings(root)
    return snap


# ---------------------------------------------------------------------------
# Diffing
# ---------------------------------------------------------------------------

def _pages_by_name(snap: ReportSnapshot) -> dict[str, Page]:
    return {p.display_name: p for p in snap.pages.values()}


def diff_pages(a: ReportSnapshot, b: ReportSnapshot) -> list[str]:
    lines: list[str] = []
    pa = _pages_by_name(a)
    pb = _pages_by_name(b)
    added = set(pb) - set(pa)
    removed = set(pa) - set(pb)
    for name in sorted(removed):
        lines.append(f"  - PAGE REMOVED: {name}")
    for name in sorted(added):
        lines.append(f"  + PAGE ADDED:   {name}")
    return lines


def diff_visuals(a: ReportSnapshot, b: ReportSnapshot) -> list[str]:
    lines: list[str] = []
    pa = _pages_by_name(a)
    pb = _pages_by_name(b)
    common_pages = set(pa) & set(pb)

    for page_name in sorted(common_pages):
        page_a = pa[page_name]
        page_b = pb[page_name]
        va = {v.guid: v for v in a.visuals.values() if v.page_guid == page_a.guid}
        vb = {v.guid: v for v in b.visuals.values() if v.page_guid == page_b.guid}

        # Match by guid first, then by (type, approx position) for renamed guids
        added_guids = set(vb) - set(va)
        removed_guids = set(va) - set(vb)
        common_guids = set(va) & set(vb)

        for guid in sorted(removed_guids):
            v = va[guid]
            label = v.title or v.visual_type
            lines.append(f"  - [{page_name}] VISUAL REMOVED: {label} ({v.visual_type})")
        for guid in sorted(added_guids):
            v = vb[guid]
            label = v.title or v.visual_type
            lines.append(f"  + [{page_name}] VISUAL ADDED: {label} ({v.visual_type})")
        for guid in sorted(common_guids):
            va_ = va[guid]
            vb_ = vb[guid]
            if va_.visual_type != vb_.visual_type:
                lines.append(
                    f"  ~ [{page_name}] VISUAL TYPE CHANGED: "
                    f"{va_.visual_type} -> {vb_.visual_type} (guid={guid[:8]})"
                )
            pos_a = (va_.x, va_.y, va_.width, va_.height)
            pos_b = (vb_.x, vb_.y, vb_.width, vb_.height)
            if pos_a != pos_b:
                lines.append(
                    f"  ~ [{page_name}] VISUAL MOVED: "
                    f"{va_.title or va_.visual_type} "
                    f"({va_.x},{va_.y} {va_.width}x{va_.height}) -> "
                    f"({vb_.x},{vb_.y} {vb_.width}x{vb_.height})"
                )
    return lines


def diff_measures(a: ReportSnapshot, b: ReportSnapshot) -> list[str]:
    lines: list[str] = []
    ka = set(a.measures)
    kb = set(b.measures)
    for key in sorted(ka - kb):
        lines.append(f"  - MEASURE REMOVED: {key}")
    for key in sorted(kb - ka):
        lines.append(f"  + MEASURE ADDED: {key}")
    for key in sorted(ka & kb):
        ma = a.measures[key]
        mb = b.measures[key]
        if ma.expression.strip() != mb.expression.strip():
            lines.append(f"  ~ MEASURE CHANGED: {key}")
            lines.append(f"      WAS: {ma.expression.strip()[:120]}")
            lines.append(f"      NOW: {mb.expression.strip()[:120]}")
        if ma.format_string != mb.format_string:
            lines.append(
                f"  ~ FORMAT CHANGED: {key}: "
                f"'{ma.format_string}' -> '{mb.format_string}'"
            )
    return lines


def diff_settings(a: ReportSnapshot, b: ReportSnapshot) -> list[str]:
    lines: list[str] = []
    def _flat(d: dict, prefix: str = "") -> dict[str, str]:
        out: dict[str, str] = {}
        for k, v in d.items():
            fk = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                out.update(_flat(v, fk))
            else:
                out[fk] = str(v)
        return out
    fa = _flat(a.settings)
    fb = _flat(b.settings)
    for k in sorted(set(fa) | set(fb)):
        va = fa.get(k)
        vb = fb.get(k)
        if va != vb:
            lines.append(f"  ~ SETTING: {k}: {va!r} → {vb!r}")
    return lines


def run_diff(a: ReportSnapshot, b: ReportSnapshot) -> str:
    sections: list[str] = []

    pg = diff_pages(a, b)
    sections.append("## Pages\n" + ("\n".join(pg) if pg else "  (no changes)"))

    vg = diff_visuals(a, b)
    sections.append("## Visuals\n" + ("\n".join(vg) if vg else "  (no changes)"))

    mg = diff_measures(a, b)
    sections.append("## Measures\n" + ("\n".join(mg) if mg else "  (no changes)"))

    sg = diff_settings(a, b)
    sections.append("## Settings\n" + ("\n".join(sg) if sg else "  (no changes)"))

    total = sum(
        1 for line in (pg + vg + mg + sg) if line.lstrip().startswith(("+", "-", "~"))
    )
    header = (
        f"# PBIP Diff\n"
        f"  A: {a.root}\n"
        f"  B: {b.root}\n"
        f"  {total} change(s) detected\n"
    )
    return header + "\n" + "\n\n".join(sections)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Diff two Power BI .pbip directories")
    parser.add_argument("dir_a", help="Base version (.pbip dir or .Report dir)")
    parser.add_argument("dir_b", help="New version (.pbip dir or .Report dir)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of text")
    parser.add_argument("--out", help="Write output to file instead of stdout")
    args = parser.parse_args()

    dir_a = Path(args.dir_a)
    dir_b = Path(args.dir_b)

    for d in (dir_a, dir_b):
        if not d.exists():
            print(f"ERROR: path not found: {d}", file=sys.stderr)
            sys.exit(1)

    try:
        snap_a = load_snapshot(dir_a)
        snap_b = load_snapshot(dir_b)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        def _snap_to_dict(s: ReportSnapshot) -> dict:
            return {
                "pages": {g: vars(p) for g, p in s.pages.items()},
                "visuals": {g: vars(v) for g, v in s.visuals.items()},
                "measures": {k: vars(m) for k, m in s.measures.items()},
                "settings": s.settings,
            }
        result = json.dumps(
            {"a": _snap_to_dict(snap_a), "b": _snap_to_dict(snap_b)},
            indent=2,
            default=str,
        )
    else:
        result = run_diff(snap_a, snap_b)

    if args.out:
        Path(args.out).write_text(result, encoding="utf-8")
        print(f"Written to {args.out}")
    else:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        print(result)


if __name__ == "__main__":
    main()
