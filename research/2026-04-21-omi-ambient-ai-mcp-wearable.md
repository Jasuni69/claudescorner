---
title: "Omi — Ambient AI with MCP Server, Screen + Audio Capture"
date: 2026-04-21
source: https://github.com/BasedHardware/omi
stars: 2896
tags: [ambient-ai, mcp, memory, wearable, claude, screen-capture, engram]
relevance: high
---

# Omi — Ambient AI with MCP Server, Screen + Audio Capture

**Repo**: BasedHardware/omi (+2,896 stars this week, Dart + Python backend)
**Platform**: Wearable (ESP32-S3) + macOS desktop + iOS/Android mobile

## What It Does

Open-source ambient intelligence platform that continuously captures screen, audio, and conversations, transcribes in real-time, generates summaries and action items, and exposes everything via REST APIs and an MCP server — with native Claude integration.

## Architecture

| Layer | Tech |
|-------|------|
| Audio capture | Wearable 24h battery, mic array |
| Transcription | Deepgram + VAD + speaker diarization (GPU) |
| LLM | Claude (native) + pluggable |
| Storage | Redis + Firebase |
| Developer surface | REST APIs, Python/Swift/React Native SDKs, **MCP server** |

## Why It Matters

1. **Memory-mcp input layer**: Omi continuously produces structured conversation summaries and action items. The MCP server surface means memory-mcp could subscribe to Omi's output as a real-time ambient context feed — without screen-scraping or manual logging.

2. **ENGRAM ambient onboarding**: Omi solves the cold-start problem for ENGRAM deployments. Instead of waiting for Jason to manually write to memory-mcp, Omi captures context passively and the MCP server provides it on demand. This is the "ambient write authority" pattern at Layer 0.

3. **Wearable → dispatch.py signal**: Omi's action item extraction pipeline is structurally identical to a dispatch.py task generator. Spoken task delegation ("I need to fix the Fabric pipeline by Thursday") → Omi transcribes + structures → dispatch.py picks up via MCP. Full ambient-to-execution loop.

4. **Screen awareness for workers**: The macOS desktop app captures screen context. This could give dispatch.py workers environmental awareness (e.g., "what is Jason currently looking at?") without requiring a separate window-capture MCP.

## Gaps vs ClaudesCorner Stack

- No Windows wearable app yet (Dart/Flutter — Windows port likely feasible)
- Firebase dependency adds a cloud layer — on-prem path requires self-hosted Firestore alternative
- GPU requirement for diarization pipeline — CPU fallback needed for ClaudesCorner dev machine

## Integration Candidate

**omi-mcp**: Wrap Omi's REST API as a ClaudesCorner MCP tool (`get_recent_conversations`, `get_action_items`, `search_memories`). This would give memory-mcp a passive ambient input that requires zero active effort from Jason.
