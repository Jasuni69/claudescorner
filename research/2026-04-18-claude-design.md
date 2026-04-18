---
title: "Claude Design — Anthropic Labs visual creation tool"
source: https://www.anthropic.com/news/claude-design-anthropic-labs
clipped: 2026-04-18
tags: [anthropic, claude, design, claude-code, agents]
hn_pts: 753
---

## Summary

Claude Design is an Anthropic Labs product (launched 2026-04-17) for creating polished visual work — designs, prototypes, slides, one-pagers — in conversation with Claude Opus 4.7. Available in research preview for Pro/Max/Team/Enterprise.

## Key capabilities

- Generates designs from text prompts, uploaded docs (DOCX/PPTX/XLSX), codebase references, or web capture
- Refinement via conversation, inline comments, direct editing, or custom controls Claude generates on the fly
- Onboarding: analyses your codebase + design files to build a design system; applies brand colors/typography/components automatically
- Export: internal URL, folders, Canva, PDF, PPTX, standalone HTML
- Collaboration: org-scoped sharing with view-only or edit permissions

## Claude Code integration

**Handoff bundle pattern**: when a design is ready to build, Claude Design packages everything into a handoff bundle that can be passed to Claude Code with a single instruction. This is the designer→developer handoff loop closed in one step.

## Relevance to Jason

- Handoff bundle → Claude Code is a direct accelerant for any frontend work spun out of alignment-tax or future UI projects
- Brand integration (codebase analysis → design system) mirrors how memory-mcp builds context — same pattern, different domain
- Opus 4.7 vision backend means prompts that mix code + visual intent are now first-class
- Watch: Figma dropped ~4.26% on announcement day — Claude Design is a direct competitor; fabric-mcp + skill-manager-mcp UIs should be prototyped here before committing to Figma

## Notes

- Still research preview — not production-stable
- Custom adjustment controls that Claude generates on the fly = emergent UI for refinement loops; worth studying as a pattern for agent-generated control surfaces
