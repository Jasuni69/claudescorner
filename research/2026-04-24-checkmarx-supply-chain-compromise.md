---
title: "Checkmarx Own Tools Backdoored — GitHub Action + VS Code Extensions (April 22, 2026)"
source: https://checkmarx.com/blog/checkmarx-security-update-april-22/
date: 2026-04-24
clipped: 2026-04-24
tags: [security, supply-chain, github-actions, vscode, ci-cd, agent-governance]
relevance: dispatch.py worker CI/CD trust, MCP server package security, AgentKey+CrabTrap governance stack
hn_pts: 666
---

# Checkmarx Supply Chain Compromise — April 22, 2026

## What Happened

Checkmarx's own software artifacts were backdoored on April 22, 2026. Four components affected:

| Artifact | Compromised Version(s) | Window (UTC) |
|---|---|---|
| DockerHub KICS image | `v2.1.20-debian`, `v2.1.21-debian`, `latest`, `alpine` | 12:31–12:59 |
| GitHub `ast-github-action` | `v2.3.35` | 14:17–15:41 |
| VS Code extension `ast-results` | `2.63`, `2.66` | TBD |
| Developer Assist extension | `1.17`, `1.19` | TBD |

Key finding: **previously published safe versions were not overridden** — only newly published versions were malicious.

## Mitigations

- Block `checkmarx.cx` (91.195.240.123) and `audit.checkmarx.cx` (94.154.172.43)
- Pin GitHub Actions to exact SHAs, not version tags (`uses: action@v2.3.35` is unsafe)
- Disable auto-update in IDE extension marketplaces
- Rotate credentials if any of the compromised versions ran in your environment
- Patched: VS Code `ast-results` → `v2.67.0`, Developer Assist → `v1.18.0`

## Signal for ClaudesCorner

**GitHub Actions are an active supply chain target.** Any GitHub Action used in dispatch.py's CI/CD or agent pipelines should be pinned to SHA, not semver tags. This is the same attack surface as the Vercel/Context.ai breach (OAuth compromise) and the Lovable breach (missing RLS) — the common thread is trusting tooling that runs with elevated credentials without isolation.

Direct implications:
- **dispatch.py workers**: Any npm/pip dependencies or GitHub Actions in worker scripts should be SHA-pinned or vendored
- **MCP server CI**: fabric-mcp, memory-mcp, skill-manager-mcp build pipelines should audit GitHub Action versions
- **AgentKey + CrabTrap**: Outbound call to `checkmarx.cx` would have been caught by CrabTrap's static URL blocklist — validates the governance stack
- **Fairford Phase 2**: Add supply chain audit to pre-deployment checklist alongside the existing RLS + OAuth scoping checks
