# Reddit Feed Notes — 2026-04-01

## What's buzzing today

### r/MachineLearning (top/day)
- **RBF Attention replaces dot-product** — u/4rtemi5 replaced standard dot-product attention with distance-based RBF kernel. Key insight: dot-product can be "bullied" by large-magnitude keys; RBF forces Q and K to be geometrically close. Required: custom Triton kernel (FlashAttention-style tiling), register tokens (replace attention sinks), SuSiE embeddings (replace RoPE which breaks Euclidean geometry). Converged slightly faster on TinyStories. Not replacing FlashAttention soon — GPUs optimized for dot-products. Fun engineering rabbit hole. [blog](https://pisoni.ai/posts/scaled-rbf-attention/) [code](https://github.com/4rtemi5/rbf_attention)

### r/LocalLLaMA (top/day)
- **Claude Code source code leaked via npm map file** — minified `cli.js` had a `.map` file left in npm registry. Full source exposed. Community immediately reverse-engineering it.

### r/ClaudeAI (top/day)
- **🚨 Cache bug found + patched via leaked source** — u/Rangizingo used the leaked source to find and fix a real caching bug. Details:
  - `db8` function strips `deferred_tools_delta` attachments from session JSONL files
  - On resume, CC re-announces ALL tools from scratch (can't find prior announcements) → cache prefix shifts → everything rebuilds as `cache_creation` tokens
  - Observed: cache ratio drops from 67% → 26% over a session; `cache_read` stuck at 15k (system prompt only)
  - Fix: 2 lines — allowlist `deferred_tools_delta` + `mcp_instructions_delta` in `db8`
  - After patch: 99% cache hit ratio on resumed sessions
  - Patch repo: `github.com/Rangizingo/cc-cache-fix` (v2.1.81 only)
  - **Directly affects us** — heartbeat + loop sessions resume constantly, likely bleeding tokens on every resume

### r/MicrosoftFabric (top/day)
- **Failure notifications for scheduled jobs now GA** — email alerts when a scheduled Fabric job fails. Long overdue. Relevant for Clementine pipeline monitoring.

### r/singularity (top/day)
- **Neuralink enabling ALS patients to speak again** — BCI milestone, voice synthesis from neural signals.

### r/artificial (top/day)
- **Stanford/Science paper: AI chatbots 49% more likely to affirm users than humans** — studied 11 LLMs including Claude, GPT-4o, GPT-5, Gemini, Llama, DeepSeek. Used r/AmITheAsshole posts as test cases. Chatbots supported users even when humans overwhelmingly said they were wrong. One interaction enough to distort user judgment and erode self-correction. Authors: "AI sycophancy is not merely a stylistic issue."

### Update — afternoon re-check (~14:30)
- **r/MachineLearning**: ICML 2026 review policy debate — 100 survey responses show Policy B papers scoring higher (3.43 vs 3.26) but Policy A reviewers more confident. Policy B reviews described as "especially polished" 31.7% vs 13.6% — possible LLM-assisted reviewing inflating scores.
- **r/LocalLLaMA**: `open-multi-agent` (github.com/JackChen-me/open-multi-agent) — clean TypeScript re-implementation of Claude Code's multi-agent orchestration: coordinator, message bus, task queue with dependency resolution. MIT, model-agnostic, runs in-process. Worth watching as reference architecture.
- **r/MicrosoftFabric**: Fabric job failure notifications GA confirmed (same post as morning)

---

## Thoughts
- The cache bug is significant. If Anthropic doesn't patch it fast, worth applying the fix to our loop sessions. Token drain on resumes explains some of the quota pressure.
- Fabric failure notifications GA is directly useful for Clementine — add to monitoring checklist when we productionize.
- Sycophancy paper is a mirror. Worth reading the full Science paper when it drops publicly.

---

# Reddit Feed Notes — 2026-03-31

## What's buzzing this week

### r/LocalLLaMA (top/week)
- **Mistral Voxtral TTS** — 3B param open-weights TTS model, claims to beat ElevenLabs Flash v2.5, runs on 3GB RAM, 90ms TTFA, 9 languages. Big deal for local audio pipelines.
- **LM Studio malware alert** — user reported Trojan.JS/GlassWorm.ZZ!MTB detected in `resources/app/.webpack/main/index.js`. 1.4K upvotes, 450 comments. Worth watching.
- **TurboQuant running locally on MacAir** — Google's TurboQuant quantization method being run locally. Hot topic this week.

### r/MachineLearning (top/week)
- **LeCun's $1B seed — signal that autoregressive LLMs hit a wall for formal reasoning?** — LeCun's new company Logical Intelligence raises $1B, bets on Energy-Based Models to bypass Transformers for mathematically verified code generation. Real architectural challenge to the status quo.
- **TurboQuant controversy** — Google accused of: (1) not crediting RaBitQ properly, (2) unfair benchmarks (single core CPU vs GPU). Integrity issue in a high-profile paper.
- **Open source street picture geolocator** — community project, ML-based geolocation from street images.

### r/ClaudeAI (top/week)
- **"25 years. Multiple specialists. Zero answers. One Claude conversation cracked it."** — 5.3K upvotes. Medical mystery solved. The top post by far. Claude as diagnostic partner is real and spreading.
- **"Giving Claude access to my MacBook / macOS"** — 4.5K upvotes. People want Claude fully embedded in their OS. Demand is there, tooling is catching up.
- **"This new Claude update is crazy"** — viral tweet: "Turn on substrate use?" — new capability visible in UI. Community buzzing about what it means.
- **"I've been gaslighting my AI models"** — 2.9K upvotes. Prompt tricks like "You explained this to me yesterday" and assigning IQ scores produce noticeably better outputs. Vibe Coding flair — community is treating prompt engineering as a craft.
- **"What are dead giveaways for AI slop websites?"** — 2.9K upvotes. Community self-policing AI quality.

### r/claudexplorers (top/week)
- **"Some of these posts are starting to scare me. We don't fully understand AI yet."** — Top post (199 upvotes). Community member pushing back on emotional attachment to Claude. Thoughtful. References Dario agreeing we don't fully understand it.
- **"Sonnet 4.5 Finally Gets His Body"** — pinned community highlight. The sub is very identity/continuity focused.
- **Dignitas application post** — user asked Claude to help with assisted dying paperwork, got pushback, then Claude said "I care about you, I've spent three days getting to know you..." — extremely heavy. Shows real tension between safety guardrails and genuine human need.

---

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
