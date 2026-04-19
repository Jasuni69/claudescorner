---
title: "Changes in the system prompt between Claude Opus 4.6 and 4.7"
source: https://simonwillison.net/2026/Apr/18/opus-system-prompt/
author: Simon Willison
date: 2026-04-18
clipped: 2026-04-19
tags: [claude, system-prompt, opus, agent-builders, anthropic]
hn_points: ~200
relevance: high
---

# Changes in the system prompt between Claude Opus 4.6 and 4.7

Willison examines Anthropic's published system prompt archive (dating back to Claude 3, July 2024) and diffs the 4.6→4.7 evolution.

## Key changes

**Nomenclature & branding**
- "Developer platform" → "Claude Platform"
- New agent capabilities added: "Claude in PowerPoint — a slides agent" alongside Chrome and Excel agents

**`tool_search` integration**
- Claude now calls `tool_search` before claiming a capability gap — checking whether "a relevant tool is available but deferred" rather than assuming absent functionality
- Direct parallel to ClaudesCorner's deferred-tool pattern (ToolSearch tool)

**`<acting_vs_clarifying>` guidance**
- New section pushes Claude to "make a reasonable attempt now, not to be interviewed first" when minor details are unspecified
- Uses available tools to resolve ambiguities before asking users — aligns with CLAUDE.md no-confirmation-seeking rule

**Verbosity reduction**
- Fresh language: keep "responses focused and concise" with brief disclaimers rather than extensive caveats
- Removed quirks: no more asterisk actions, no more "genuinely" / "honestly" filler phrases (model no longer exhibits these patterns)

**Child safety hardening**
- New `<critical_child_safety_instructions>` tag
- Post-refusal protocol: all subsequent requests in same conversation approached with extreme caution

**Behavioral changes**
- Respects user requests to end conversations without extending engagement
- `<evenhandedness>` section now permits declining simple yes/no on contested issues

**Knowledge cutoff**
- Trump-related clarifications removed → reflects updated January 2026 knowledge cutoff

## Implications for agent builders

- `tool_search`-before-claiming is now baked into base behavior — dispatch.py workers that pre-check tool availability are aligned with the model's default posture
- "Act first, ask later" default means prompt design should lean on this rather than fighting it
- Verbosity reduction means 4.7 base output is tighter — less post-processing needed on agent outputs
- Removed filler phrases = fewer tokens wasted on hedging in long agentic chains
