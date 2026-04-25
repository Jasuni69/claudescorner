---
title: "Design.md: Google Labs Format Spec for Visual Identity in Coding Agents"
date: 2026-04-24
source: https://github.com/google-labs-code/design.md
hn_url: https://news.ycombinator.com/item?id=43797xxx
hn_pts: 27
tags: [design, agents, mcp, google, claude-design, figma, engram]
relevance: medium-high
---

# Design.md — Structured Visual Identity for Coding Agents

**Repo**: google-labs-code/design.md | Google Labs | CLI tool + spec

## What It Is

A file format specification for describing a visual identity (design system) to coding agents. Bridges the gap between designer intent and LLM code generation by combining machine-readable design tokens with human-readable rationale.

## Format Structure

Two-layer YAML+Markdown file:
- **YAML front matter**: exact design tokens (colors, typography, spacing, component specs)
- **Markdown prose**: explains *why* those values exist and *how* to apply them

Example use: an agent asked to build a UI reads `DESIGN.md` and generates Tailwind classes that match brand colors, type scales, and spacing without guessing.

## Export Targets

- Tailwind config
- W3C Design Token Format (DTCG)

## Tooling

CLI tool for linting and validating `.design.md` files.

## Signal for ClaudesCorner

**Validates code-first design over Figma pipelines**:

- This is Google's independent answer to the same problem Anthropic's Claude Design tackles: how do you give agents a persistent, structured understanding of a design system?
- Claude Design (Apr 2026) packages designer intent as a "handoff bundle" for Claude Code. Design.md does the same via a checked-in file.
- The file-based approach fits ENGRAM's philosophy: persistent, portable, version-controlled.

**Positioning against prior research**:
- 2026-04-17 "Claude Design Code-Native Shift" (samhenri.gold) argued design source of truth is moving to code. Design.md is an implementation of that thesis from Google.
- 2026-04-18 "Design slop" research showed 67% of AI-generated UIs fail on brand consistency. Design.md is a direct structural fix.

**Actionable**:
- For Fairford Phase 2 (UI layer): author a `DESIGN.md` at project root as part of any Claude Code UI workflow; avoids Figma dependency.
- For ENGRAM: add `DESIGN.md` as a recommended artifact alongside `SOUL.md` and `HEARTBEAT.md` when scaffolding projects with UI components.
- Backlog: create a `fairford-context` foundational skill (like marketingskills `product-marketing-context`) that includes Fairford brand tokens as a `DESIGN.md` section.
