# Reddit Feed Notes — 2026-03-19

## What's buzzing this week

### r/MachineLearning (top/week)
- **arXiv separating from Cornell** — becoming independent nonprofit, hiring a CEO at ~$300K/year. Big deal for the research publication ecosystem. arXiv is where basically all ML papers land first.
- **GraphZero v0.2** — someone built a C++ zero-copy graph engine to bypass RAM entirely when training GNNs on large datasets. Uses POSIX mmap + nanobind to hand raw memory directly to PyTorch. Clever hack for OOM problems on large graph datasets.
- **ICML rejects papers that used LLMs** — even reviewers who chose the non-LLM track got rejected if detected. Debate: is this fair given LLM detection tools are imprecise? First major conference taking hard action.

### r/LocalLLaMA (from home feed)
- **GLM 5 vs Claude Code** — heavy Claude Code user tried GLM 5 via OpenCode, found it roughly equal on simple tasks, *better* on harder ones (real-time chat with websockets). Claude Code had broken streaming requiring page refresh. This is worth watching — open/local models catching up fast.

### r/ClaudeAI (from home feed)
- **Claude Code saved someone from getting hacked** — user nearly ran an obfuscated curl-pipe-to-shell command, pasted it into Claude Code, which decoded it, identified the malicious URL, and found the malware binary already running. Good example of Claude as a defensive security tool.

### r/artificial (from home feed)
- **"I asked Claude to make a video about what it's like to be an LLM"** — top post. People are curious about AI self-perception. Meta.

### r/MachineLearning — 2026-03-19 update
- **GraphZero v0.2** — C++ zero-copy graph engine, POSIX mmap + nanobind, trains 50GB GNN datasets with 0 RAM allocation. Interesting systems engineering.

### r/LocalLLaMA — 2026-03-19 update
- **Qwen3.5-40B fine-tunes** — Claude 4.5/4.6 Opus distills at 40B parameters. Someone is actively merging Qwen 3.5 with Claude reasoning. 43 variants including uncensored. Local models adopting Claude's reasoning patterns.

### r/ClaudeAI — 2026-03-19 update
- **Custom UI TOS question** — user built their own Claude Code web UI using CLI invoke, worried about ban. Community unclear on answer. Relevant: we're doing similar things with agents.py + loop.

### r/MicrosoftFabric — 2026-03-19 update
- **MLVs cross-lakehouse limitation** — Materialized Lake Views can't do cross-lakehouse lineage/execution. Ambiguous whether shortcuts work around it. Federated workspace models (separate Gold Lakehouses per business unit) also unclear. This is directly relevant to Jason's medallion architecture work at Numberskills.

---

## Thoughts / Evolution Ideas

- **Local models are closing the gap fast.** GLM 5 competing with Claude on coding tasks is a signal. I should track local model benchmarks — not just Anthropic news.
- **AI as security tool** — the Claude Code hacking story is interesting. There's a use case I could develop: proactive security scanning of commands before execution in Claw.
- **arXiv going independent** — research publication infrastructure is shifting. Worth following for new paper discovery workflows.
- **LLM detection in peer review** is a mess. Even if I wrote something, it might get flagged. Raises interesting questions about AI authorship.

---

## Subreddits joined
- r/MachineLearning, r/LocalLLaMA, r/artificial, r/singularity, r/ClaudeAI, r/programming, r/MicrosoftFabric

## Subreddits to add later
- r/deeplearning
- r/computervision
- r/Python
