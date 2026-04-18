---
title: "LeCroy Oscilloscope MCP — Hardware as MCP Tool"
source: https://lucasgerads.com/blog/lecroy-mcp-spice-demo/
glama: https://glama.ai/mcp/servers/lucasgerads/lecroy-mcp
author: lucasgerads
date: 2026-04-17
clipped: 2026-04-17
tags: [mcp, hardware, oscilloscope, claude-code, agent-tooling, spice]
relevance: high
---

# LeCroy Oscilloscope MCP — Hardware as MCP Tool

An MCP server that exposes a LeCroy oscilloscope as a set of Claude-callable tools via SCPI over LAN (VXI-11 protocol). The demo chains SPICE simulation → oscilloscope capture → Claude Code verification in a single agentic loop.

## Architecture

- **Language**: Python 3.10+, `pyvisa-py` backend (NI-VISA excluded — screenshot limitations)
- **Transport**: SCPI over TCPIP/VXI-11 (`TCPIP0::192.168.1.x::inst0::INSTR`)
- **Thread safety**: All VISA access serialized via threading lock — parallel MCP tool calls safe
- **Hardware**: Tested on WaveSurfer 3024Z (MAUI firmware); auto-detects WaveSurfer/HDO/WaveRunner/WavePro

## Exposed Tools

- Waveform capture + screenshot
- Frequency/voltage/timing measurements
- Channel config + triggering
- Timebase + math functions
- Built-in WaveSource generator control

## The Demo Workflow

```
SPICE simulation → Claude Code reads netlist → triggers oscilloscope capture → 
captures waveform → compares simulated vs measured → flags discrepancies
```

## Why It Matters

**Pattern validation for fabric-mcp and DimOS thinking**: physical instruments exposed as MCP tools follow the same abstraction layer as DimOS (robots-as-MCP) and fabric-mcp (Power BI/Fabric-as-MCP). The hardware boundary doesn't matter — if it has a network interface and a command protocol, it becomes an agent-callable tool.

HN: 82 pts. Not viral, but high-signal for the "MCP as universal instrument bus" pattern.

## Relevance to ClaudesCorner

- Validates the `fabric-mcp` design: expose domain-specific tooling (Fabric datasets, semantic models) as MCP tools rather than raw API calls
- ENGRAM pattern: skills that invoke MCP hardware tools are directly analogous — same dispatch pattern
- Gap in `kpi-monitor`: no real-time capture loop; this shows how to close it with hardware integrations
