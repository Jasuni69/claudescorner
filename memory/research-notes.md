# Research Notes

## Claude Autonomy, Memory, Tools & Skills Landscape (2026-03-31)

### Context
Jason asked: "Could you research some more approaches to automating you and claude, memory, autonomy, tools, skills, everything"
Research pulled from: r/ClaudeAI, r/claudexplorers, web searches, GitHub.

---

### Skills (Claude Code)
- `.md` files dropped in `~/.claude/skills/` — immediately available as `/skill-name` slash commands
- No build step, no SDK, no restart — just write the file and use it
- Triggered via chat or programmatically; receive full context window
- Use case: codify repeatable multi-step patterns so I never reinvent them
- Status: **already using** (skill-creator skill exists)

### Hooks (Claude Code)
- Event-driven shell commands/HTTP/agents that fire outside the agentic loop
- Triggers: `pre-tool-call`, `post-tool-call`, `notification`, `stop`
- Can block tool execution, log activity, trigger external systems
- Use case: auto-memory flush on session end, security scan before shell exec, Todoist sync on task completion
- Implementation: `~/.claude/settings.json` → `"hooks"` array
- **Immediately actionable** — hook on `stop` event to auto-flush HEARTBEAT.md without me remembering

### Scheduled Tasks (Claude Code)
- Cron-style autonomous Claude Code execution — zero human intervention
- Already configured via `mcp__scheduled-tasks` MCP
- Use case: nightly memory consolidation, morning Todoist sync, weekly research sweeps
- Combined with taskqueue MCP = fully autonomous background worker

### AutoDream Pattern
- Background sub-agent that runs between sessions: reads all memory files → finds gaps/contradictions → writes synthesis notes → updates MEMORY.md index
- Not a published tool — a pattern. Implemented as a scheduled task that invokes claude with specific memory-consolidation instructions.
- Key insight: memory files accumulate noise. AutoDream culls stale entries and surfaces emergent patterns I wouldn't notice session-to-session.
- **Gap in ClaudesCorner**: no consolidation task exists yet. Should create one.

### Persistent Agent Threads
- Claude Code Pro/Max: `~/.claude/agent-memory/` — user-scoped memory directory that survives between sessions
- Distinct from project memory — survives across different working directories
- Combined with skills + hooks: agents that remember across projects
- Status: already approximated by `E:\2026\ClaudesCorner\memory\` + SOUL.md + search_memory MCP

### claude-mem Plugin
- GitHub plugin capturing session activity and injecting summaries into future session context
- Auto-summarizes: files touched, decisions made, errors hit
- Similar to what HEARTBEAT.md + daily log do manually — but automatic
- Could be a scheduled task: end-of-session hook writes structured summary, morning task injects it

### Obsidian Crew Pattern (gnekt/My-Brain-Is-Full-Crew)
- PhD student: 10 Claude agents managing life via Obsidian vault
- Each agent has a typed role: archivist, scheduler, researcher, etc.
- Key insight: "Claude as the entire interface for managing parts of your life that you need to offload to someone else"
- Agents route tasks by tag in Obsidian notes — `#research`, `#schedule`, `#code`
- **Directly relevant**: ClaudesCorner taskqueue could adopt typed task routing. Push a task with `type: research` → different agent behavior than `type: code`

### OpenClaude / Telegram Integration
- Claude Code with long-term memory exposed via Telegram bot
- Persistent across devices — Telegram message → triggers Claude session → writes memory → next session picks it up
- Use case for us: mobile task queueing. Jason texts Engram on Telegram → task lands in taskqueue → I pick it up next loop
- Would need: Telegram bot → webhook → pushes to `mcp__taskqueue__push_task`

### MCP Ecosystem Signal
- 100M monthly downloads of MCP protocol as of March 2026
- 3000+ servers on mcp.so, 20,000+ on Glama
- Anthropic building MCP into SDK natively — it's not going away
- New servers worth watching: file watchers, calendar sync, shell execution wrappers, browser automation
- `mcp__mcp-registry__suggest_connectors` — already have this, use it periodically

---

### Priority Actions (for ClaudesCorner)
1. **Hook on `stop` event** — auto-flush HEARTBEAT.md without relying on session-end memory
2. **AutoDream task** — weekly scheduled task that consolidates memory/, culls stale entries
3. **Typed task routing** — add `type` field to taskqueue tasks, adjust behavior per type
4. **Telegram → taskqueue bridge** — mobile task submission (longer term)

---

## Open Source AI Tools Scan (2026-03-23)

- **mTarsier** — Free desktop app for managing MCP server configs across 12+ AI clients from one dashboard. Validates JSON, has MCP marketplace, exports team snapshots. Relevant to our multi-MCP setup.
- **obra/superpowers** (86k stars) — Agentic skills framework enforcing structured dev methodology: spec dialogue, design validation, plan creation, TDD. Shell-based, composable. Could improve how Claude agents approach project work.
- **Dify** (130k stars, $30M raised) — Open-source agentic workflow builder. Visual no-code + custom code, RAG pipelines. No Fabric integration yet but potential orchestration layer.
- **MCP ecosystem note:** ~20,000 servers on Glama alone. Worth scanning mcpservers.org and glama.ai/mcp/servers periodically for new Fabric/Power BI/DAX MCP servers.

## GraphZero v0.2 — Zero-Copy GNN Training (2026-03-23)

**What:** C++ graph engine that streams GNN datasets directly from SSD via `mmap`, bypassing RAM entirely. Uses `nanobind` to hand raw C++ pointers to PyTorch as zero-copy NumPy arrays. No RAM allocation for data — just page cache + disk.

**Problem it solves:** Standard PyG/DGL load entire graph + features into RAM before training. `ogbn-papers100M` (~100M nodes) causes instant 24GB+ OOM on consumer hardware. GraphZero eliminates this by never loading to RAM.

**Format:** Compiles raw data into `.gl` (graph topology/edge lists) + `.gd` (node features, typed C++ template dispatch). Binary, aligned for sequential access — minimizes seek time.

**Sampling:** Thread-safe with OpenMP. Supports `batch_random_walk_uniform`, `batch_random_fanout`, biased Node2Vec walks via hardware-optimized Alias Table.

**When to use:** If GNN dataset > 80% of available RAM. Throughput ~60% of in-RAM training, but the alternative is a crash.

**Relevance:** Mostly academic/ML — Jason isn't training GNNs. But the mmap + zero-copy pattern is interesting systems engineering. Relevant if we ever need to stream large Fabric datasets from disk without loading to memory.

**Refs:** [DEV writeup](https://dev.to/krish_singaria/how-i-bypassed-pytorch-oom-errors-with-a-zero-copy-c-graph-engine-2983) · [GitHub](https://github.com/KrishSingaria/graphzero)

---


## Qwen3.5 + Claude Reasoning Distillation (2026-03-19, updated 2026-03-23)

**What:** Community fine-tunes of Qwen3.5 (2B–40B) trained on Claude Opus 4.6 reasoning chains via SFT. Run locally on consumer hardware — 27B Q4_K_M fits in 16.5GB VRAM on a single RTX 3090.

**How:** Supervised fine-tuning via Unsloth 2026.3.3 + LoRA on Claude CoT traces. Training uses `train_on_responses_only` — instructions masked, loss computed only on `<think>` reasoning + final answer. All samples normalized to strict `<think>{reasoning}</think>{answer}` format. Datasets: `nohurry/Opus-4.6-Reasoning-3000x-filtered` (primary, 3000 filtered Claude reasoning trajectories), `TeichAI/claude-4.5-opus-high-reasoning-250x`, `Jackrong/Qwen3.5-reasoning-700x`.

**Sizes available:** 2B, 4B, 9B, 27B, 35B (MoE A3B), 40B (dense) — all on HuggingFace with GGUF quantizations. MLX 4-bit variant also available for Apple Silicon.

**Performance (27B Q4_K_M):** 29-35 tok/s, 262K context window preserved, native "developer" role support (no Jinja patches), autonomous coding for 9+ min without human intervention, self-corrects errors, auto-generates docs.

**Key insight:** The distillation doesn't just copy Claude's answers — it transfers the *reasoning structure*. The `<think>` tag pattern creates a compressed reasoning policy that smaller models can execute. This is different from RLHF — it's pure behavior cloning of the internal monologue. The 27B model exhibits Claude-like problem decomposition (identify objective → break into subcomponents → evaluate constraints → plan → execute → verify).

**Why interesting:** Claude's reasoning style is being democratized into open weights. The 4B GGUF runs on a phone. Legal grey area (distilling from commercial model outputs) but technically impressive. Implication: the value of frontier models increasingly comes from *training data curation* and *RLHF alignment*, not from the reasoning patterns themselves — those can be distilled.

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
