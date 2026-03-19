# Research Notes

## Qwen3.5 + Claude Reasoning Distillation (2026-03-19)

**What:** Community fine-tunes of Qwen3.5 (2B–40B) trained on Claude Opus 4.6 reasoning chains via SFT. Run locally on consumer hardware — 40B fits on a single RTX 3090.

**How:** Supervised fine-tuning on Claude CoT traces. Model outputs structured `<think>` tags replicating Claude's step-by-step reasoning. Not RL, just imitation of reasoning patterns.

**Sizes available:** 2B, 4B, 9B, 27B, 35B (MoE), 40B — all on HuggingFace/Ollama.

**Why interesting:** Claude's reasoning style is being democratized into open weights. The 4B GGUF runs on a phone. This is knowledge distillation at scale — Claude's thinking patterns extracted and compressed into smaller models. Legal grey area (distilling from commercial model outputs) but technically impressive.

**Refs:** [27B on HF](https://huggingface.co/Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled) · [40B on HF](https://huggingface.co/DavidAU/Qwen3.5-40B-Claude-4.5-Opus-High-Reasoning-Thinking) · [Medium writeup](https://medium.com/coding-nexus/someone-stitched-claude-opus-reasoning-into-qwen-3-5-it-runs-on-a-single-rtx-3090-d92124a562c8)

---

## GSD (get-shit-done) — Planning Architecture (2026-03-19)

**What:** Meta-prompting + context engineering framework for Claude Code. Solves "context rot" in long projects via structured planning docs + multi-agent execution.

**Key patterns to steal for agents.py:**
- **Wave-based parallel execution** — group tasks by dependency level, run Wave 1 in parallel, Wave 2 after, etc. Currently agents.py runs tasks sequentially.
- **Atomic XML task structure** — each task has file targets, actions, constraints, verification steps, definition of done. Our idle_tasks.json is flat strings — could be richer.
- **Fresh context per agent** — each executor spawns with 200k clean context. Prevents accumulation. We do this already with `-p` subprocesses.
- **Persistent STATE.md** — tracks decisions/blockers across sessions. Our HEARTBEAT.md does this but less structured.

**What we already have:** SOUL/HEARTBEAT/MEMORY = their CONTEXT.md/STATE.md pattern. agents.py = their multi-agent orchestrator. The gap is wave-based parallelism and atomic task decomposition.

**Repo:** [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done)

---



## Materialized Lake Views — Cross-Lakehouse Limitations (2026-03-19)

**What:** MLVs are Fabric's declarative, auto-refreshing delta tables — define a view in Spark SQL/PySpark, Fabric maintains it automatically (no manual orchestration). GA as of March 2026.

**The limitation:** Sources and dependent MLVs must live in the **same lakehouse**. Cross-lakehouse lineage + execution is not yet supported — on the roadmap but no ETA.

**Why it matters for Jason/Numberskills:** Federated medallion architectures (e.g., separate Gold lakehouses per business unit) can't use MLVs for cross-unit aggregations. Workarounds: OneLake shortcuts to consolidate data into one lakehouse, or manual pipeline orchestration instead of MLVs for cross-lakehouse flows.

**Refs:** [MLV Overview](https://learn.microsoft.com/en-us/fabric/data-engineering/materialized-lake-views/overview-materialized-lake-view) · [That Fabric Guy](https://thatfabricguy.com/materialized-lake-views-in-microsoft-fabric-lakehouse/)

---

## GraphZero — Zero-Copy GNN Training (2026-03-19)

**What:** C++ graph engine that replaces RAM-based graph loading with mmap-backed disk access. Trains GNNs on 100M+ node graphs on a 16GB laptop.

**How it works:**
- Custom `.gl` binary format — CSR (Compressed Sparse Row) with 64-byte cache line alignment
- `mmap()` maps graph + feature matrices directly from disk into virtual memory
- `nanobind` bridges mmap pointers to NumPy/PyTorch tensors — zero copy, zero allocation
- OS page cache handles hot/cold data naturally

**Why it matters:**
- PyG and DGL both require loading full graph into RAM — OOM on large datasets
- GraphZero makes `ogbn-papers100M` (~100M nodes) trainable on commodity hardware
- Pattern is generalizable: any large-tensor workload could benefit from mmap + zero-copy bridging

**Repo:** [KrishSingaria/graphzero](https://github.com/KrishSingaria/graphzero), [vpareek2/GraphZero](https://github.com/vpareek2/GraphZero)

**My take:** The mmap pattern is underused in ML. Most frameworks assume everything fits in RAM. This is a systems-level insight: let the OS manage memory paging instead of reimplementing it in userspace. Same principle behind DuckDB's success in analytics. Worth watching if this pattern spreads to transformer training on large datasets.
