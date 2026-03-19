# Research Notes

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
