# MarkItDown × bi-agent Integration Evaluation
**Date:** 2026-04-17  
**Question:** Can a PDF/DOCX→Markdown pipeline feed schema context to bi_agent.py?

---

## What MarkItDown Is

`microsoft/markitdown` converts documents (PDF, DOCX, PPTX, XLSX, HTML, CSV, JSON, audio, images, YouTube URLs) to Markdown. It is a broad-format text scraper, not a structured data extractor.

**Install:** `pip install markitdown`  
**Python API:**
```python
from markitdown import MarkItDown
md = MarkItDown()
result = md.convert("document.pdf")
print(result.text_content)  # raw Markdown string
```

---

## MCP Server: YES (Official)

Microsoft ships an official MCP server: `pip install markitdown-mcp`

**Exposes one tool:** `convert_to_markdown(uri)` — accepts `http://`, `https://`, `file://`, and `data:` URIs.

**Wire into Claude Code settings.json:**
```json
{
  "mcpServers": {
    "markitdown": {
      "command": "markitdown-mcp"
    }
  }
}
```

Docker variant also available. No config beyond install.

---

## Current bi-agent Schema Pattern

`bi_agent.py` consumes a typed dict:
```json
{
  "tables": [
    {
      "name": "Sales",
      "columns": ["OrderDate", "Amount", "Region"],
      "measures": ["Total Revenue"],
      "is_date_table": false
    }
  ]
}
```

`schema_to_prompt()` (line 51) serializes this to a Markdown block injected into the Claude system prompt with `cache_control: ephemeral`. The schema must be **structured JSON** — not raw prose.

---

## Table/Schema Extraction Quality: POOR for PDF

| Format | MarkItDown Quality | Notes |
|--------|-------------------|-------|
| XLSX   | Good              | Native row/column → Markdown table |
| DOCX   | Moderate          | Preserves simple tables; merged cells break |
| PDF    | Poor              | Linearizes columns; table structure lost |
| HTML   | Good              | Structural tags preserved |
| CSV    | Good              | Direct conversion |

PDF is the worst case: MarkItDown reads the PDF text stream, which may extract an entire column (all dates, then all descriptions) before the next column — breaking row integrity. Tables with merged cells, multi-line rows, or complex styling are mangled.

**Docling** (IBM, HuggingFace-backed) uses ML table detection (TableFormer) and produces significantly higher fidelity. ~100x slower, ~1–2GB model download, but preserves row/column structure reliably.

---

## Fitness Verdict

### Use MarkItDown for bi-agent? Conditional.

| Scenario | Fit | Notes |
|----------|-----|-------|
| XLSX schema export (e.g., from Fabric metadata download) | **Yes** | Best path: export schema to Excel, convert via MarkItDown, parse the table |
| DOCX schema documentation (simple tables) | **Partial** | Works if tables are plain; add post-processing to reconstruct JSON |
| PDF data dictionary / ERD export | **No** | Table structure loss is too high; wrong column assignments silently corrupt DAX |
| HTML Power BI documentation pages | **Yes** | Clean conversion; parseable |
| Native Fabric API (REST/SQL) | **Preferred** | No document round-trip needed at all |

---

## Recommended Integration Architecture

### Tier 1 (preferred): Native schema extraction
Use `fabric-mcp` or Power BI REST API to pull schema directly. No document conversion needed. Already partially wired via `projects/fabric-mcp/server.py`.

### Tier 2: XLSX pipeline (safe document path)
```
Fabric metadata export (XLSX)
  → markitdown.convert("schema.xlsx")
  → parse Markdown table → build schema dict
  → pass to bi_agent.py --schema schema.json
```
This is reliable because XLSX → Markdown preserves structure.

### Tier 3: Docling for PDF (when doc is only source)
```
PDF data dictionary
  → docling.DocumentConverter().convert("schema.pdf")
  → extract TableItem objects → build schema dict
  → pass to bi_agent.py --schema schema.json
```
Add `pip install docling`. Slower first run (model download). Worth it for PDFs.

### Avoid
- MarkItDown on PDF for schema extraction (silent data corruption)
- Passing raw Markdown prose as schema — `schema_to_prompt()` expects a typed dict

---

## Quick Win: Wire MCP Server for General Ingestion

Even if MarkItDown isn't the schema extraction path, the MCP server is useful for:
- Feeding supporting documents (business context, glossaries, KPI definitions) to Claude without manual copy-paste
- Pre-processing meeting notes or spec docs before a bi-agent session

Install: `pip install markitdown-mcp`, add to `settings.json` → Claude gets `convert_to_markdown` as a tool mid-session.

---

## Action Items

- [ ] Wire `markitdown-mcp` into Claude Code `settings.json` for general document ingestion
- [ ] Add `--docling` flag to bi_agent.py for PDF schema input (Tier 3 path)  
- [ ] XLSX→schema JSON helper script for Tier 2 path (25 lines, parse Markdown table)
- [ ] Evaluate fabric-mcp schema pull as primary path (avoids document round-trip entirely)

---

## Verification Notes (2026-04-17)

Confirmed via `bi_agent.py` read:
- Schema loaded at line ~186: `json.loads(Path(args.schema).read_text(encoding="utf-8"))`
- `schema_to_prompt()` is defined around line 51; schema injected into system prompt with `cache_control: {"type": "ephemeral"}`
- docstring already lists `--docling` as planned flag: `python bi_agent.py --docling report.pdf "total sales by region"` — action item above tracks actual implementation
- MOCK_SCHEMA has 5 tables: Sales, Customers, Products, Date, Budget
