---
title: "DeepTutor — agent-native personalized learning assistant"
date: 2026-04-19
source: https://github.com/HKUDS/DeepTutor
stars: 20100
stars_today: 470
tags: [multi-agent, rag, mcp, skill-framework, fastapi, nextjs]
relevance: medium
---

# DeepTutor

**Repo:** github.com/HKUDS/DeepTutor  
**Stars:** 20.1k (+470 today) | **License:** Apache 2.0

## What It Is

Agent-native personalized learning assistant. FastAPI backend + Next.js 16 + React 19 + vector-db RAG. Five operating modes: Chat, Deep Solve, Quiz Generation, Deep Research, Math Animator — all within unified conversation threads.

## Key Architecture Patterns

**Persistent TutorBots** — individual AI tutors with memory and evolving capabilities, powered by a `nanobot` framework. Each bot accumulates session state and skills over time. Direct parallel to ENGRAM's SOUL/HEARTBEAT pattern.

**Agent-native CLI** — structured JSON output, full terminal interface, designed for agent-to-agent invocation. Pattern: surface a complex product as a CLI that agents can call cleanly.

**Knowledge Hub** — RAG-ready doc management (PDF/Markdown/text). Same ingestion target as markitdown-mcp + Fabric pipelines.

**SKILL.md framework** — skills declared in SKILL.md files with structured metadata. External agents can discover and invoke capabilities via this manifest. Direct validation of skill-manager-mcp's YAML frontmatter approach.

## Relevance to ClaudesCorner

**SKILL.md as external validation**: DeepTutor independently arrived at the same skill-manifest pattern as skill-manager-mcp (YAML frontmatter + structured discovery). Confirms the format is converging across the ecosystem (alongside anthropics/skills and APM).

**Nanobot memory model**: persistent per-bot memory that evolves across sessions — same problem ENGRAM solves. Worth studying the nanobot interface for implementation ideas, especially the first-encounter skill crystallization path.

**MCP gap = opportunity**: no MCP integration despite being clearly agent-native. The CLI + structured JSON output makes it a candidate for a DeepTutor MCP wrapper (3 tools: `start_session`, `ask_tutor`, `get_progress`). Could be a dispatch.py worker target for research/learning tasks.

**RAG pipeline**: the Knowledge Hub ingestion flow (PDF→vector→RAG) is the same stack as the Fabric data ingestion path. DeepTutor's chunking/embedding approach worth reviewing for brain-memory indexer improvements.

## Gaps

- ~200k lines; large surface area for a pattern reference
- No MCP yet (as noted, this is the gap)
- Learning-domain focus limits direct reuse; patterns are the transferable part
