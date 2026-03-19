# DAX Notes

*Updated: 2026-03-19*

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

## Resources

- [DAX Patterns](https://www.daxpatterns.com/) — canonical reference
- [DAX Guide](https://dax.guide/) — function reference
- [Time Intelligence Patterns 2026](https://powerbiconsulting.com/blog/time-intelligence-dax-patterns-2026)
- [DAX Patterns 2026 book](https://www.amazon.com/DAX-Patterns-2026-Intelligence-Analytics/dp/B0GGLLFP6G) — 50 copy-paste formulas
