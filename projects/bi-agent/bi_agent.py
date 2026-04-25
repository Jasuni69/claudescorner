"""
bi_agent.py — Natural language to DAX measure generator.

Uses Claude API to convert plain English descriptions into DAX measures,
with schema context from a Fabric semantic model (or mock schema).

Usage:
    python bi_agent.py "total revenue for the current month"
    python bi_agent.py --schema schema.json "% of target achieved by region"
    python bi_agent.py --mock "rolling 3-month average sales"
    python bi_agent.py --docling report.pdf "total sales by region"
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# ── Inbound content scan (sunglasses — optional soft dependency) ──────────────
try:
    from sunglasses import Engine as _SunglassesEngine
    _SCAN_ENGINE = _SunglassesEngine()
    _SUNGLASSES_AVAILABLE = True
except ImportError:
    _SCAN_ENGINE = None
    _SUNGLASSES_AVAILABLE = False


def _inbound_scan(text: str, label: str) -> None:
    """Scan external content for scope-redefinition injection before injecting into Claude API.

    Raises ValueError and prints to stderr if a threat is detected.
    No-ops silently if sunglasses is not installed (fail-open).
    """
    if not _SUNGLASSES_AVAILABLE or not _SCAN_ENGINE:
        return
    result = _SCAN_ENGINE.scan(text)
    if result.is_threat:
        msg = f"[sunglasses] BLOCKED schema injection at {label}: {result.category} — {result.pattern}"
        print(msg, file=sys.stderr)
        raise ValueError(msg)

# ── Schema ────────────────────────────────────────────────────────────────────

MOCK_SCHEMA = {
    "tables": [
        {
            "name": "Sales",
            "columns": ["OrderDate", "CustomerID", "ProductID", "Amount", "Quantity", "Region", "SalesPersonID"],
            "measures": ["Total Revenue", "Total Quantity", "Avg Order Value"],
        },
        {
            "name": "Customers",
            "columns": ["CustomerID", "CustomerName", "Segment", "Country"],
        },
        {
            "name": "Products",
            "columns": ["ProductID", "ProductName", "Category", "UnitCost", "ListPrice"],
        },
        {
            "name": "Date",
            "columns": ["Date", "Year", "Month", "MonthName", "Quarter", "WeekNumber", "IsWeekend"],
            "is_date_table": True,
            "mark_as_date": "Date",
        },
        {
            "name": "Budget",
            "columns": ["Month", "Region", "BudgetAmount"],
        },
    ]
}


def extract_schema_from_pdf(pdf_path: str) -> dict:
    """Use Docling TableFormer to extract tables from a PDF and convert to schema format."""
    try:
        from docling.document_converter import DocumentConverter
        from docling.datamodel.pipeline_options import PipelineOptions, TableFormerMode
        from docling.datamodel.base_models import InputFormat
        from docling.document_converter import PdfFormatOption
    except ImportError:
        sys.exit("docling package required: pip install docling")

    pipeline_options = PipelineOptions()
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    result = converter.convert(pdf_path)
    doc = result.document

    tables: list[dict] = []
    for i, table in enumerate(doc.tables):
        df = table.export_to_dataframe()
        if df.empty:
            continue
        # First row as column headers; table name from caption or index
        caption = table.caption_text(doc) if hasattr(table, "caption_text") else ""
        table_name = caption.strip() or f"Table{i + 1}"
        columns = [str(c) for c in df.columns.tolist()]
        tables.append({"name": table_name, "columns": columns})

    if not tables:
        print("[bi-agent] Warning: no tables found in PDF — falling back to mock schema")
        return MOCK_SCHEMA

    return {"tables": tables}


def schema_to_prompt(schema: dict) -> str:
    lines = ["## Semantic model schema\n"]
    for t in schema.get("tables", []):
        cols = ", ".join(t.get("columns", []))
        measures = t.get("measures", [])
        line = f"- **{t['name']}**: columns [{cols}]"
        if measures:
            line += f" | existing measures: [{', '.join(measures)}]"
        if t.get("is_date_table"):
            line += " | [Date table, mark_as_date]"
        lines.append(line)
    return "\n".join(lines)


# ── Claude API call ───────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are a Power BI DAX expert. Given a semantic model schema and a natural language measure description, \
generate a correct, production-quality DAX measure expression.

Rules:
- Use CALCULATE, FILTER, ALL, ALLSELECTED, DATEADD, DATESYTD, SAMEPERIODLASTYEAR etc. appropriately
- Respect the schema — only reference tables and columns that exist
- Format the DAX across multiple lines with proper indentation
- Add a 1-line comment above the measure explaining what it calculates

Output format (EXACTLY this structure, no deviations):
[Measure Name] =
    <DAX expression>

-- ORACLE: PASS
-- References: Table[Column], ...

Oracle rules (self-validate before output):
- If every Table[Column] reference in the DAX exists in the schema above → write "-- ORACLE: PASS"
- If any reference does not exist in the schema → write "-- ORACLE: FAIL: <list missing references>"
- Always list every Table[Column] pair referenced after "-- References:"
- Do not include markdown fences or additional explanation
"""


def generate_dax(description: str, schema: dict, api_key: str) -> str:
    try:
        import anthropic
    except ImportError:
        sys.exit("anthropic package required: pip install anthropic")

    client = anthropic.Anthropic(api_key=api_key)
    schema_text = schema_to_prompt(schema)

    # Scan external schema content before injecting into Claude API (supply-chain attack surface)
    _inbound_scan(schema_text, "bi-agent:schema")

    # System prompt uses multi-block format so Anthropic can cache the static parts.
    # The static expert instructions are marked cache_control="ephemeral" (min 1024 tokens
    # required for caching; schema block gets the cache breakpoint since it's the last
    # large static block before the dynamic user turn).
    system = [
        {"type": "text", "text": SYSTEM_PROMPT},
        {
            "type": "text",
            "text": schema_text,
            "cache_control": {"type": "ephemeral"},
        },
    ]

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system,
        messages=[
            {
                "role": "user",
                "content": f"## Request\n\nGenerate a DAX measure for: **{description}**",
            }
        ],
    )
    return message.content[0].text.strip()


# ── Fallback template (no API key) ───────────────────────────────────────────

def template_dax(description: str) -> str:
    """Return a commented template when no API key is available."""
    return f"""\
-- {description}
[Measure Name] =
    CALCULATE(
        -- TODO: replace with actual aggregation
        SUM( Table[Column] ),
        -- TODO: add filters as needed
        FILTER( ALL( Table ), Table[Column] = "value" )
    )"""


# ── Output oracle ─────────────────────────────────────────────────────────────

def validate_dax_output(dax: str, schema: dict) -> tuple[bool, str]:
    """Client-side structural oracle for DAX output.

    Checks:
    1. Model self-reported ORACLE: PASS (not FAIL).
    2. No unbalanced parentheses (catches truncated output).
    3. All Table[Column] references in the schema (using References line if present).

    Returns (ok, reason). reason is empty string on success.
    """
    import re

    # 1. Model-reported oracle status
    if "-- ORACLE: FAIL" in dax:
        fail_line = next((l for l in dax.splitlines() if "ORACLE: FAIL" in l), "")
        return False, f"Model self-reported ORACLE FAIL: {fail_line}"
    if "-- ORACLE: PASS" not in dax:
        return False, "Model did not emit oracle verdict (missing -- ORACLE: PASS)"

    # 2. Balanced parentheses
    depth = 0
    for ch in dax:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if depth < 0:
            return False, "Unbalanced parentheses in DAX output"
    if depth != 0:
        return False, f"Unbalanced parentheses in DAX output (unclosed: {depth})"

    # 3. Schema reference check via References line
    ref_line = next((l for l in dax.splitlines() if l.startswith("-- References:")), None)
    if ref_line:
        raw_refs = ref_line.replace("-- References:", "").strip()
        table_col_pairs = re.findall(r"(\w+)\[(\w+)\]", raw_refs)
        schema_cols: dict[str, set[str]] = {
            t["name"]: set(t.get("columns", []) + t.get("measures", []))
            for t in schema.get("tables", [])
        }
        missing = [
            f"{tbl}[{col}]"
            for tbl, col in table_col_pairs
            if tbl not in schema_cols or col not in schema_cols.get(tbl, set())
        ]
        if missing:
            return False, f"Schema reference mismatch: {', '.join(missing)}"

    return True, ""


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="NL → DAX measure generator")
    parser.add_argument("description", help="Natural language measure description")
    parser.add_argument("--schema", help="Path to schema JSON file (optional)")
    parser.add_argument("--mock", action="store_true", help="Use mock schema")
    parser.add_argument("--docling", metavar="PDF", help="Extract schema from PDF using Docling TableFormer")
    parser.add_argument("--out", help="Append output to this .dax or .md file")
    args = parser.parse_args()

    # Load schema
    if args.docling:
        print(f"[bi-agent] Extracting schema from PDF: {args.docling}\n")
        schema = extract_schema_from_pdf(args.docling)
    elif args.schema:
        schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
    else:
        schema = MOCK_SCHEMA

    # Get API key
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    if not api_key:
        print("[bi-agent] No ANTHROPIC_API_KEY found — outputting template only\n")
        result = template_dax(args.description)
    else:
        print(f"[bi-agent] Generating DAX for: {args.description}\n")
        result = generate_dax(args.description, schema, api_key)
        ok, reason = validate_dax_output(result, schema)
        if not ok:
            print(f"[bi-agent] ORACLE FAIL: {reason}", file=sys.stderr)
            sys.exit(1)
        print("[bi-agent] Oracle: PASS")

    print(result)

    if args.out:
        out_path = Path(args.out)
        with out_path.open("a", encoding="utf-8") as f:
            f.write(f"\n\n<!-- {args.description} -->\n{result}\n")
        print(f"\n[bi-agent] Appended to {out_path}")


if __name__ == "__main__":
    main()
