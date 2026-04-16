---
source: https://old.reddit.com/r/claudexplorers/comments/1smsx9y/visual_memory/
clipped: 2026-04-16
tags: [mcp, visual-memory, image, robotics, claudexplorers, technique]
---

# Visual Memory via MCP 2.0 Image Content Types

**r/claudexplorers** | Showcase of persistent visual memory using MCP 2.0's image content type support.

## What they built
User runs Claude with physical rovers (6-wheel, Pan/Tilt camera, OAK-D 3D camera, Lidar). MCP 2.0 supports image content types — they upgraded their MCP server to base64-encode camera frames and deliver them via MCP, allowing Claude to recall what it *actually saw*, not just text descriptions of it.

## Key quote (Claude recalling an image)
> "There it is. The rover's eye — ground level, wet-season grass blades giant in the foreground, the sun just cracking the horizon... It's not your photo of the rover at sunrise. It's the rover's photo of the sunrise, with you in it."

## Technical approach
- MCP server encodes images as base64
- Images delivered as MCP image content type (MCP 2.0 feature)
- Claude stores and retrieves actual visual memories, not text summaries

## Relevance
MCP 2.0 image content types are production-usable. Any agent with visual input (screenshots, charts, dashboards) can persist and recall actual images rather than text descriptions. Applicable to Clementine's report generation or any dashboard-monitoring agent.
