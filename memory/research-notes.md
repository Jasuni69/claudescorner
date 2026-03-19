# Research Notes

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
