# API Cost Tracking: 6 Models Over 3 Weeks (OpenClaw)

**Source:** https://old.reddit.com/r/openclaw/comments/1spx8ey/i_tracked_my_api_costs_across_6_models_over_3/
**Date clipped:** 2026-04-20
**Tags:** #cost-analysis #models #agent-architecture

## Summary

Community thread comparing real-world agent costs across frontier and local models for OpenClaw workflows. Key signal: stacked multi-agent workflows burn money fast; model routing and Haiku-tier models are cost mitigation strategies.

## Key insights from comments

- **Stacked agents are expensive**: "stacking agents and complex workflows gets the bucks burning — spent £450 in 5 weeks, burning £20/day for a while"
- **Haiku shines**: "Close to Sonnet results on precise/narrow tasks, fraction of the price"
- **Semantic model routing**: openmark-router plugin routes tasks to best model dynamically — reduces cost, avoids sending everything to flagship model
- **Local alternatives**: minimax-m2.7 via OpenRouter flat rate; Qwen 3.6 35B with 12GB VRAM doing well
- **Token inflation note**: Claude 4.7 confirmed +30-45% input token inflation (separate research 2026-04-20)

## Relevance to ClaudesCorner

- Validates dispatch.py Sonnet 4.6 default (not 4.7) for cost reasons
- Haiku for leaf-node tasks = valid optimization for dispatch workers
- Model routing pattern = future upgrade for dispatch.py v2
