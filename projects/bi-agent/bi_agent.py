"""
bi_agent.py — Natural language to DAX measure generator.

Uses Claude API to convert plain English descriptions into DAX measures,
with schema context from a Fabric semantic model (or mock schema).

Usage:
    python bi_agent.py "total revenue for the current month"
    python bi_agent.py --schema schema.json "% of target achieved by region"
    python bi_agent.py --mock "rolling 3-month average sales"
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

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
- Output ONLY: measure name (as [Measure Name]) on line 1, then the DAX expression
- Do not include markdown fences or explanation — just the measure name and DAX
"""


def generate_dax(description: str, schema: dict, api_key: str) -> str:
    try:
        import anthropic
    except ImportError:
        sys.exit("anthropic package required: pip install anthropic")

    client = anthropic.Anthropic(api_key=api_key)
    schema_text = schema_to_prompt(schema)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"{schema_text}\n\n## Request\n\nGenerate a DAX measure for: **{description}**",
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


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="NL → DAX measure generator")
    parser.add_argument("description", help="Natural language measure description")
    parser.add_argument("--schema", help="Path to schema JSON file (optional)")
    parser.add_argument("--mock", action="store_true", help="Use mock schema")
    parser.add_argument("--out", help="Append output to this .dax or .md file")
    args = parser.parse_args()

    # Load schema
    if args.schema:
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

    print(result)

    if args.out:
        out_path = Path(args.out)
        with out_path.open("a", encoding="utf-8") as f:
            f.write(f"\n\n<!-- {args.description} -->\n{result}\n")
        print(f"\n[bi-agent] Appended to {out_path}")


if __name__ == "__main__":
    main()
