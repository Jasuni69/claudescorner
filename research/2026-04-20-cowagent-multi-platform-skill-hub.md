---
title: CowAgent — Multi-Platform Agent with Skill Hub and Vector Memory
date: 2026-04-20
source: github.com/zhayujie/CowAgent
tags: [agent, skill-hub, vector-memory, multi-platform, claude, mcp, wechat, feishu]
stars: 43545
weekly_gain: +566
---

# CowAgent — Multi-Platform Agent with Skill Hub and Vector Memory

**Repo:** github.com/zhayujie/CowAgent  
**Stars:** 43,545 | Weekly gain: +566  
**License:** MIT  
**Trending:** GitHub Python weekly (2026-04-20, position ~4)

## What It Is

CowAgent is a production-deployed multi-platform AI assistant + extensible agent framework. It bridges consumer messaging platforms (WeChat, Feishu, DingTalk, Enterprise WeChat, QQ, WeChat Official Accounts) with LLM providers, adding persistent memory, tool execution, and a skill marketplace on top.

## Architecture

### Platform Layer
- WeChat, Feishu, DingTalk, Enterprise WeChat, QQ, WeChat Official Accounts, web interface
- Linux / macOS / Windows

### LLM Support
- Claude, GPT series, Gemini, DeepSeek, MiniMax, Qwen, GLM, Kimi/Moonshot, Doubao
- Unified via LinkAI interface — model switching without code changes

### Memory System
- Persistent conversation storage
- Keyword search + **vector search** over history
- Per-user memory isolation across platforms

### Agent Framework
- Multi-turn task planning with tool calling
- Up to **20 decision steps** per task
- Built-in tools: file operations, terminal execution, browser automation, scheduled tasks
- Multimodal: text, images, audio, files

### Skill System
- **Skill Hub**: one-click install from hub or GitHub URL
- **Conversation-driven skill creation**: describe a skill in chat → CowAgent scaffolds it
- Skill categories: data retrieval, automation, integrations

## Signal for ClaudesCorner

### Validates skill-manager-mcp design
CowAgent's Skill Hub is an independent convergence on the same pattern as skill-manager-mcp: semantic skill discovery + one-click install + conversation-driven creation. Key differences:
- CowAgent: file-based skill store, no semantic search
- skill-manager-mcp: FTS5 + vector search over skill bodies = **differentiated**

### Gap: No MCP layer
CowAgent has no MCP server exposure. Its 43k-star install base across Chinese enterprise platforms (Feishu/DingTalk = dominant in CN enterprise) represents a potential MCP wrapper opportunity — a `cowagent-mcp` could expose its skill catalog and memory as MCP tools.

### Platform-as-distribution pattern
CowAgent's approach — embed agent into existing messaging apps rather than building a new UI — is the opposite of Thunderbolt/Mozilla (standalone client). For Fairford deployment in a corporate context, a Feishu/Teams integration following CowAgent's pattern may be more adoption-friendly than a standalone UI.

### Conversation-driven skill creation
The ability to create skills through natural conversation (not YAML authoring) is a UX pattern skill-manager-mcp currently lacks. Worth evaluating as a `skill_create_from_description` tool that wraps an LLM call.

## Gaps vs ClaudesCorner Stack
| Feature | CowAgent | ClaudesCorner |
|---|---|---|
| MCP native | No | Yes (memory-mcp, skill-manager-mcp) |
| Semantic skill search | No (keyword only) | Yes (FTS5 + vector) |
| Dispatch / parallel workers | No | Yes (dispatch.py) |
| Platform integrations | WeChat/Feishu/DingTalk | None (terminal only) |
| Conversation-driven skill creation | Yes | No |
| Vector memory | Yes | Yes (vectorstore.db) |

## Related Clips
- [skill-manager-mcp](../projects/skill-manager-mcp/) — closest analog
- [Hermes Agent](2026-04-20-hermes-agent-102k.md) — also has skill creation loop
- [DeepTutor SKILL.md](2026-04-19-deeptutor-agent-native-learning.md) — YAML manifest pattern
