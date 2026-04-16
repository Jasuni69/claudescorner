---
source: https://old.reddit.com/r/openclaw/comments/1smuktf/anyone_separating_agent_memory_like_this/
clipped: 2026-04-16
tags: [agent-architecture, memory, knowledge-graph, openclaw]
---

# Anyone separating agent + memory like this?

**r/openclaw** | Discussion on clean architectural split between agent execution layer and persistent memory layer.

## Pattern
```
Outer infra = agent layer   → decisions, actions, tool calls
Inner infra = LLM wiki      → linked markdown, entity notes, evolving summaries
```

Instead of cramming memory into the agent loop, the agent *manages* the knowledge layer as a separate concern.

- **agent** = actions
- **wiki** = long-term memory

Inspired by Hermes-style agents that decide what to ingest, query, and update in the knowledge store.

## Why it's cleaner
- Agent loop stays stateless/lightweight
- Memory evolves independently of agent prompts
- Knowledge can be queried by multiple agents without coupling

## Relevance
This mirrors the ClaudesCorner SOUL/HEARTBEAT/memory file split — worth formalizing the "wiki" layer as structured linked notes rather than flat JSON.
