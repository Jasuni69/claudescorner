# DAX Notes

*Updated: 2026-03-31*

## March 2026 Updates

- **Custom Totals** (new in March 2026) — override measure's default total in tables/matrices without a separate measure variant
- **Integer surrogate keys** for relationships — 3-5x faster VertiPaq joins vs string keys
- **Disable Auto Date/Time** — prevents hidden date tables bloating model size
- **COALESCE, WINDOW, NETWORKDAYS** now available as modern DAX functions
- **Copilot pattern**: keep core measures lean (Sales, Quantity, Profit) — let Copilot generate YTD/MTD/QTD variants rather than pre-building them all

*Updated: 2026-03-23*

## Time Intelligence Patterns (2026)

**YTD / QTD / MTD**
- `TOTALYTD`, `TOTALQTD`, `TOTALMTD` — simplest approach for standard calendars
- Always require a marked Date Table — never use auto date/time (bloats model)
- Fiscal year support: third parameter on TOTALYTD

**Same Period Last Year**
- `SAMEPERIODLASTYEAR` — shifts current filter context back exactly 1 year
- `DATEADD` — more flexible, custom intervals (quarters, months, days)

**Rolling Averages**
- `CALCULATE` + `DATESINPERIOD` — rolling window of any size
- Common: 3-month, 12-month rolling

**Running Totals**
- `CALCULATE` + `FILTER` on date table — accumulate from fixed start date

## Core Best Practices

- **VAR** everywhere — calculate once, reuse. Improves perf + readability.
- **Star schema** — VertiPaq optimized for it. Can reduce model size 60%, 10x query speed.
- **Core measures** first — build `[Sales]`, `[Quantity]`, `[Profit]` then derive YTD/MTD from them. Don't create parallel measure trees.
- Mark Date Table explicitly in Power BI.

## 2026 New Functions

- **NAMEOF / TABLEOF** — reference model objects safely. Auto-adapts to renames. Works in UDFs. Replaces fragile string-based patterns.
- **INFO.USERDEFINEDFUNCTIONS()** — (preview, March 2026) returns metadata about UDFs in the model. DAX UDFs now track rename dependencies automatically, same as measures/columns.
- **New types:** `CalendarRef`, `ColumnRef`, `MeasureRef`, `TableRef` — first-class type refs for use inside UDFs. More expressive than string references.

## March 2026 Report Features

- **Custom Totals** — override a visual's aggregation logic per-visual without changing the underlying DAX measure. No more duplicate measures just to fix a total row.
- **Series label leader lines** — cosmetic but useful for dense line charts.
- **Copilot DAX query refinement** — Copilot can now write and refine DAX queries in DAX query view. Lean schemas (fewer ambiguous table/column names) dramatically improve accuracy.

## Resources

- [DAX Patterns](https://www.daxpatterns.com/) — canonical reference
- [DAX Guide](https://dax.guide/) — function reference
- [Time Intelligence Patterns 2026](https://powerbiconsulting.com/blog/time-intelligence-dax-patterns-2026)
- [DAX Patterns 2026 book](https://www.amazon.com/DAX-Patterns-2026-Intelligence-Analytics/dp/B0GGLLFP6G) — 50 copy-paste formulas
