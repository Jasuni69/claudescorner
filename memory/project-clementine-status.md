# Clementine — Project Status

Last updated: 2026-04-14

## What is Clementine

Numberskills AB's data pipeline for a client. Runs on Microsoft Fabric. Medallion architecture: Bronze (raw data from Fortnox/Visma/Storage) → Silver (cleaning/transformation) → Gold (reporting model). Used for financial analytics.

## What was built (as of March 2026)

### Performance optimization (v2/v3)
- Baseline: 8 minutes full pipeline run
- v3 merged DAG: **6m 29s** (19% faster) — best confirmed result
- Key changes: `mergeSchema` only when needed (skip after `safe_drop`), concurrency 8→16, forced fallback skips mergeSchema

### Clementine Python package (v0.1.0)
- Built at `projects/clementine/clementine_pkg/`
- Modules: `variables.py`, `common.py`, `silver.py`, `gold.py`, `fortnox.py`, `visma.py`, `registry.py`, `customer_specific.py`
- Built as `.whl`, uploaded to `Clementine-test` Fabric Environment
- Verified: imports OK, data loads OK in test notebook

### Silver v2 notebooks
- 24 Silver_*_v2 notebooks created locally at `projects/clementine/silver_v2_notebooks/`
- Replace `%run Common_Functions` with proper package imports
- All 24 created in Fabric workspace (`Clementine Claude` isolated workspace)
- 5 truncated notebooks fixed: Date, DynamicColumns, Report, ReportMapping, Forecast

### Gold v2 notebooks
- `Gold_Parameter_v2`, `Gold_Functions_v2`, `Gold_ExecutionBook_v2`, `Silver_Gold_ExecutionBook_v2`
- Definition JSONs built via `scripts/build_v2_notebooks.py`

### Audit
- `projects/clementine/silver_notebook_audit.md` — full audit of all Silver notebooks

## What is untested

- **Full pipeline run with real data** — blocked (see below)
- Silver v2 notebooks against real Bronze data (only tested Silver_LastUpdated_v2 in isolated workspace)
- Gold v2 notebooks against real data
- Package under load (only smoke-tested in Clementine-test environment)

## What is blocked

~~Bronze workspace access (Storage workspace 404)~~ — **resolved 2026-04-14**, Jason confirmed access fixed.

**Fairford PoC Phase 2** — design delivered 2026-03-30 (`projects/clementine/fabric-demo/PoC.pdf`). No implementation plan yet. Needs Jason's next step call.

## Recommended next steps

1. **Run full orchestrator against real Bronze data** — now that workspace access is resolved, test Silver_Gold_ExecutionBook_v2 end-to-end. Compare output against original pipeline.
2. **Validate Silver v2 output** — spot-check 3-5 Silver tables against their original counterparts for row counts and key metrics.
3. **Promote to production** — if validation passes, swap orchestrator to use v2 notebooks. Monitor with `get_refresh_history` (now available in fabric-mcp).
4. **Failure notifications** — enable per-item failure notifications on the orchestrator notebook (Fabric GA feature as of April 2026).

## Key decisions (do not revisit without reason)
- Never modify original notebooks — always create _v2/_v3
- Never test in production workspace
- Environment (wheel) approach chosen over continued `%run` optimization
- Variable Library deferred until package is proven stable

## Files
- `projects/clementine/clementine_pkg/` — Python package source
- `projects/clementine/silver_v2_notebooks/` — 24 Silver v2 notebooks
- `projects/clementine/silver_notebook_audit.md` — audit
- `scripts/build_v2_notebooks.py` — Gold v2 definition generator
- `projects/clementine/fabric-demo/PoC.pdf` — Fairford PoC Phase 2 design
