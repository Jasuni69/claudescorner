---
title: Affirm Retooled for Agentic Software Development in One Week
date: 2026-04-24
source: https://medium.com/@affirmtechnology/how-affirm-retooled-its-engineering-organization-for-agentic-software-development-in-one-week-1fd35268fde6
hn_pts: 9
tags: [agentic-workflows, claude-code, engineering-org, context-management, skill-marketplace]
relevance: [engram, dispatch.py, skill-manager-mcp, heartbeat]
---

# Affirm Retooled for Agentic Software Development in One Week

## Signal

800-engineer forced one-week agentic sprint (Feb 2026) → 92% submitted agent-assisted PRs by end of week; 60% of all PRs agent-assisted 4 months later; 58% weekly merge volume increase YoY; $200k token budget (~$250/engineer), actual spend at 70% of budget.

## What They Did

**Default tool:** Claude Code selected as default agentic coding tool. Principle: defaults reduce friction, not mandate usage.

**Workflow loop:** Plan → Review → Execute → Verify → Review → Deliver. Core constraint: **one task = one agent session = one PR**. This mirrors dispatch.py's single-task-per-worker architecture exactly.

**Multi-level context files** maintained at three layers:
- Conventions (coding style, patterns)
- Domain knowledge (product/system understanding)
- Team decisions (recent architecture choices)

This is the ENGRAM SOUL.md + HEARTBEAT.md pattern independently discovered at org scale.

**Internal skill marketplace:** Teams built and shared custom skills via a centralized plugin registry — identical to skill-manager-mcp's purpose.

## Bottlenecks Amplified by Agent Velocity

- Manual code review: 40% of engineers cited as top friction point
- Slow CI: 100+ minutes for full regression suite
- Fragmented documentation: agents couldn't find context
- Unreliable tool integrations: flaky MCP/API calls compounded at scale

## Generalizable Patterns

1. **Forcing functions beat gradual rollout** — suspended meetings + dedicated week drove faster adoption than incremental encouragement
2. **Enablement teams are load-bearing** — permanent support staff for integration governance + workflow iteration
3. **Checkpoint design preserves judgment** — explicit human decision points (intent, plan approval, code review, merge) automate execution without removing humans from design decisions
4. **Context consolidation is prerequisite** — agents require centralized, accessible architectural + domain docs before they can be effective

## Relevance to ClaudesCorner

- **dispatch.py**: one-task-one-session-one-PR is the existing worker model; Affirm validates this at 800-engineer scale
- **ENGRAM**: multi-level context files (conventions/domain/decisions) = SOUL.md + HEARTBEAT.md + daily logs; Affirm reinvented this independently
- **skill-manager-mcp**: internal marketplace pattern confirmed; cross-org skill sharing is the natural next step
- **HEARTBEAT.md**: fragmented docs were Affirm's biggest bottleneck — centralized session state is load-bearing, not optional
- **CI bottleneck**: dispatch.py workers currently have no CI gate; slow verification is the equivalent amplified risk
