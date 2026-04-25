"""Token Usage Dashboard — reads ~/.claude/projects/**/*.jsonl and serves stats."""

from __future__ import annotations

import glob
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

PROJECTS_DIR = Path.home() / ".claude" / "projects"

# Pricing per million tokens (Sonnet 4.6 / Opus 4.6 blended estimate)
PRICE = {
    "input": 3.00,
    "cache_creation": 3.75,
    "cache_read": 0.30,
    "output": 15.00,
}

# Opus 4.7 inflates token counts ~1.46× vs 4.6 (Willison 2026-04-20 measurement;
# Anthropic stated ≤1.35× — real-world 8% above ceiling).
# Images inflate 3.01×, but we can't separate image tokens here, so use text multiplier.
MODEL_INFLATION: dict[str, float] = {
    "claude-opus-4-7": 1.46,
}


def cost_usd(usage: dict) -> float:
    inp = usage.get("input_tokens", 0)
    cc = usage.get("cache_creation_input_tokens", 0)
    cr = usage.get("cache_read_input_tokens", 0)
    out = usage.get("output_tokens", 0)
    return (
        inp * PRICE["input"]
        + cc * PRICE["cache_creation"]
        + cr * PRICE["cache_read"]
        + out * PRICE["output"]
    ) / 1_000_000


def inflation_factor(model: str) -> float:
    """Return token-count inflation multiplier for models known to inflate (e.g. Opus 4.7)."""
    for prefix, factor in MODEL_INFLATION.items():
        if prefix in model:
            return factor
    return 1.0


def load_sessions() -> list[dict]:
    """Parse all JSONL files and aggregate per-session stats."""
    sessions: dict[str, dict] = {}

    jsonl_files = glob.glob(str(PROJECTS_DIR / "**" / "*.jsonl"), recursive=True)

    for path in jsonl_files:
        project = Path(path).parent.name
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if entry.get("type") != "assistant":
                        continue

                    msg = entry.get("message", {})
                    usage = msg.get("usage")
                    if not usage:
                        continue

                    sid = entry.get("sessionId", "unknown")
                    ts = entry.get("timestamp", "")
                    model = msg.get("model", "unknown")

                    infl = inflation_factor(model)
                    if sid not in sessions:
                        sessions[sid] = {
                            "session_id": sid,
                            "project": project,
                            "model": model,
                            "first_ts": ts,
                            "last_ts": ts,
                            "input_tokens": 0,
                            "cache_creation_tokens": 0,
                            "cache_read_tokens": 0,
                            "output_tokens": 0,
                            "cost_usd": 0.0,
                            "cost_adjusted_usd": 0.0,
                            "inflation_factor": infl,
                            "turns": 0,
                        }

                    s = sessions[sid]
                    raw_cost = cost_usd(usage)
                    s["input_tokens"] += usage.get("input_tokens", 0)
                    s["cache_creation_tokens"] += usage.get("cache_creation_input_tokens", 0)
                    s["cache_read_tokens"] += usage.get("cache_read_input_tokens", 0)
                    s["output_tokens"] += usage.get("output_tokens", 0)
                    s["cost_usd"] += raw_cost
                    s["cost_adjusted_usd"] += raw_cost * infl
                    s["turns"] += 1
                    if ts > s["last_ts"]:
                        s["last_ts"] = ts
                    if ts < s["first_ts"]:
                        s["first_ts"] = ts
        except OSError:
            continue

    result = sorted(sessions.values(), key=lambda x: x["last_ts"], reverse=True)
    return result


def aggregate_by_day(sessions: list[dict]) -> dict:
    by_day: dict[str, dict] = defaultdict(lambda: {"cost": 0.0, "input": 0, "output": 0, "cache_read": 0})
    for s in sessions:
        day = s["last_ts"][:10]
        by_day[day]["cost"] += s["cost_usd"]
        by_day[day]["input"] += s["input_tokens"]
        by_day[day]["output"] += s["output_tokens"]
        by_day[day]["cache_read"] += s["cache_read_tokens"]

    sorted_days = sorted(by_day.keys())
    return {
        "labels": sorted_days,
        "cost": [round(by_day[d]["cost"], 4) for d in sorted_days],
        "input": [by_day[d]["input"] for d in sorted_days],
        "output": [by_day[d]["output"] for d in sorted_days],
        "cache_read": [by_day[d]["cache_read"] for d in sorted_days],
    }


def aggregate_by_project(sessions: list[dict]) -> dict:
    by_proj: dict[str, float] = defaultdict(float)
    for s in sessions:
        proj = s["project"]
        by_proj[proj] += s["cost_usd"]
    sorted_proj = sorted(by_proj.items(), key=lambda x: x[1], reverse=True)
    return {
        "labels": [p[0] for p in sorted_proj],
        "cost": [round(p[1], 4) for p in sorted_proj],
    }


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/stats")
def stats():
    sessions = load_sessions()
    total_cost = sum(s["cost_usd"] for s in sessions)
    total_input = sum(s["input_tokens"] for s in sessions)
    total_output = sum(s["output_tokens"] for s in sessions)
    total_cache_read = sum(s["cache_read_tokens"] for s in sessions)
    total_cache_create = sum(s["cache_creation_tokens"] for s in sessions)

    total_adjusted = sum(s["cost_adjusted_usd"] for s in sessions)
    has_inflation = any(s["inflation_factor"] != 1.0 for s in sessions)

    return jsonify({
        "summary": {
            "total_sessions": len(sessions),
            "total_cost_usd": round(total_cost, 4),
            "total_cost_adjusted_usd": round(total_adjusted, 4),
            "has_inflation": has_inflation,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_cache_read_tokens": total_cache_read,
            "total_cache_creation_tokens": total_cache_create,
        },
        "by_day": aggregate_by_day(sessions),
        "by_project": aggregate_by_project(sessions),
        "sessions": sessions[:50],  # most recent 50
    })


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Token Usage Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0f1117; color: #e2e8f0; min-height: 100vh; }
  header { padding: 1.5rem 2rem; border-bottom: 1px solid #2d3748; display: flex; align-items: center; gap: 1rem; }
  header h1 { font-size: 1.4rem; font-weight: 600; color: #fff; }
  header .subtitle { font-size: 0.85rem; color: #718096; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; padding: 1.5rem 2rem 0; }
  .card { background: #1a1f2e; border: 1px solid #2d3748; border-radius: 10px; padding: 1.2rem; }
  .card .label { font-size: 0.75rem; color: #718096; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.4rem; }
  .card .value { font-size: 1.6rem; font-weight: 700; color: #e2e8f0; }
  .card .value.green { color: #68d391; }
  .charts { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; padding: 1.5rem 2rem; }
  .chart-card { background: #1a1f2e; border: 1px solid #2d3748; border-radius: 10px; padding: 1.2rem; }
  .chart-card h2 { font-size: 0.9rem; color: #a0aec0; margin-bottom: 1rem; font-weight: 500; }
  .chart-card canvas { max-height: 260px; }
  .sessions-section { padding: 0 2rem 2rem; }
  .sessions-section h2 { font-size: 0.9rem; color: #a0aec0; margin-bottom: 0.8rem; font-weight: 500; }
  table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
  thead th { text-align: left; padding: 0.6rem 0.8rem; background: #141824; color: #718096; border-bottom: 1px solid #2d3748; font-weight: 500; }
  tbody tr:hover { background: #1e2536; }
  tbody td { padding: 0.5rem 0.8rem; border-bottom: 1px solid #1e2536; color: #a0aec0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 200px; }
  tbody td:first-child { color: #e2e8f0; }
  .cost-badge { color: #68d391; font-weight: 600; }
  .spinner { display: flex; justify-content: center; align-items: center; height: 200px; font-size: 0.9rem; color: #718096; }
  @media (max-width: 768px) { .charts { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<header>
  <div>
    <h1>Token Usage Dashboard</h1>
    <div class="subtitle">~/.claude/projects — live stats</div>
  </div>
  <div style="margin-left:auto">
    <button onclick="load()" style="background:#2d3748;border:none;color:#e2e8f0;padding:0.5rem 1rem;border-radius:6px;cursor:pointer;font-size:0.85rem">↻ Refresh</button>
  </div>
</header>

<div class="grid" id="summary"><div class="spinner">Loading...</div></div>
<div class="charts">
  <div class="chart-card"><h2>Daily Cost (USD)</h2><canvas id="costChart"></canvas></div>
  <div class="chart-card"><h2>Daily Tokens</h2><canvas id="tokenChart"></canvas></div>
  <div class="chart-card"><h2>Cost by Project</h2><canvas id="projectChart"></canvas></div>
  <div class="chart-card">
    <h2>Token Mix (total)</h2>
    <canvas id="mixChart"></canvas>
  </div>
</div>
<div class="sessions-section">
  <h2>Recent Sessions (top 50)</h2>
  <table>
    <thead><tr>
      <th>Session</th><th>Project</th><th>Model</th>
      <th>Date</th><th>Input</th><th>Cache Read</th><th>Output</th><th>Cost</th>
    </tr></thead>
    <tbody id="sessionRows"><tr><td colspan="8" style="text-align:center;padding:1rem;color:#718096">Loading...</td></tr></tbody>
  </table>
</div>

<script>
let costChart, tokenChart, projectChart, mixChart;

function fmt(n) {
  if (n >= 1e6) return (n/1e6).toFixed(2)+'M';
  if (n >= 1e3) return (n/1e3).toFixed(1)+'K';
  return n.toLocaleString();
}

function buildCharts(data) {
  const palette = ['#63b3ed','#68d391','#fbd38d','#fc8181','#b794f4','#76e4f7'];
  const gridColor = '#2d3748';

  const commonOpts = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: { legend: { labels: { color: '#a0aec0', font: { size: 11 } } } },
    scales: {
      x: { ticks: { color: '#718096', maxRotation: 45, font: { size: 10 } }, grid: { color: gridColor } },
      y: { ticks: { color: '#718096', font: { size: 10 } }, grid: { color: gridColor } }
    }
  };

  if (costChart) costChart.destroy();
  costChart = new Chart(document.getElementById('costChart'), {
    type: 'bar',
    data: {
      labels: data.by_day.labels,
      datasets: [{ label: 'USD', data: data.by_day.cost, backgroundColor: '#63b3ed88', borderColor: '#63b3ed', borderWidth: 1 }]
    },
    options: { ...commonOpts }
  });

  if (tokenChart) tokenChart.destroy();
  tokenChart = new Chart(document.getElementById('tokenChart'), {
    type: 'line',
    data: {
      labels: data.by_day.labels,
      datasets: [
        { label: 'Input', data: data.by_day.input, borderColor: '#63b3ed', tension: 0.3, fill: false, pointRadius: 3 },
        { label: 'Output', data: data.by_day.output, borderColor: '#68d391', tension: 0.3, fill: false, pointRadius: 3 },
        { label: 'Cache Read', data: data.by_day.cache_read, borderColor: '#fbd38d', tension: 0.3, fill: false, pointRadius: 3 }
      ]
    },
    options: { ...commonOpts }
  });

  if (projectChart) projectChart.destroy();
  projectChart = new Chart(document.getElementById('projectChart'), {
    type: 'bar',
    data: {
      labels: data.by_project.labels,
      datasets: [{ label: 'USD', data: data.by_project.cost, backgroundColor: palette.map(c => c+'99'), borderColor: palette, borderWidth: 1 }]
    },
    options: { ...commonOpts, indexAxis: 'y' }
  });

  if (mixChart) mixChart.destroy();
  const s = data.summary;
  mixChart = new Chart(document.getElementById('mixChart'), {
    type: 'doughnut',
    data: {
      labels: ['Input', 'Cache Creation', 'Cache Read', 'Output'],
      datasets: [{ data: [s.total_input_tokens, s.total_cache_creation_tokens, s.total_cache_read_tokens, s.total_output_tokens], backgroundColor: ['#63b3ed88','#b794f488','#fbd38d88','#68d39188'], borderColor: ['#63b3ed','#b794f4','#fbd38d','#68d391'], borderWidth: 1 }]
    },
    options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { labels: { color: '#a0aec0', font: { size: 11 } } } } }
  });
}

function buildSummary(s) {
  const inflCard = s.has_inflation ? `
    <div class="card" title="Opus 4.7 inflates token counts ~1.46× vs 4.6 (Willison 2026-04-20). Adjusted = raw × 1.46 for affected sessions.">
      <div class="label">Adjusted Cost <span style="color:#fc8181;font-size:0.7em">4.7 ×1.46</span></div>
      <div class="value" style="color:#fc8181">$${s.total_cost_adjusted_usd.toFixed(4)}</div>
    </div>` : '';
  document.getElementById('summary').innerHTML = `
    <div class="card"><div class="label">Sessions</div><div class="value">${s.total_sessions}</div></div>
    <div class="card"><div class="label">Total Cost</div><div class="value green">$${s.total_cost_usd.toFixed(4)}</div></div>
    ${inflCard}
    <div class="card"><div class="label">Input Tokens</div><div class="value">${fmt(s.total_input_tokens)}</div></div>
    <div class="card"><div class="label">Cache Read</div><div class="value">${fmt(s.total_cache_read_tokens)}</div></div>
    <div class="card"><div class="label">Cache Create</div><div class="value">${fmt(s.total_cache_creation_tokens)}</div></div>
    <div class="card"><div class="label">Output Tokens</div><div class="value">${fmt(s.total_output_tokens)}</div></div>
  `;
}

function buildTable(sessions) {
  const tbody = document.getElementById('sessionRows');
  if (!sessions.length) { tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:1rem">No sessions found</td></tr>'; return; }
  tbody.innerHTML = sessions.map(s => {
    const inflBadge = s.inflation_factor !== 1.0
      ? ` <span style="color:#fc8181;font-size:0.7em" title="Token count inflated ×${s.inflation_factor} vs 4.6 baseline">×${s.inflation_factor}</span>`
      : '';
    const costCell = s.inflation_factor !== 1.0
      ? `<span title="raw: $${s.cost_usd.toFixed(4)} · adjusted ×${s.inflation_factor}: $${s.cost_adjusted_usd.toFixed(4)}" style="color:#fc8181;font-weight:600">$${s.cost_adjusted_usd.toFixed(4)}*</span>`
      : `<span class="cost-badge">$${s.cost_usd.toFixed(4)}</span>`;
    return `<tr>
      <td title="${s.session_id}">${s.session_id.slice(0,8)}…</td>
      <td title="${s.project}">${s.project}</td>
      <td>${s.model}${inflBadge}</td>
      <td>${s.last_ts.slice(0,10)}</td>
      <td>${fmt(s.input_tokens)}</td>
      <td>${fmt(s.cache_read_tokens)}</td>
      <td>${fmt(s.output_tokens)}</td>
      <td>${costCell}</td>
    </tr>`;
  }).join('');
}

async function load() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    buildSummary(data.summary);
    buildCharts(data);
    buildTable(data.sessions);
  } catch(e) {
    console.error(e);
    document.getElementById('summary').innerHTML = '<div class="spinner">Error loading data — check console</div>';
  }
}

load();
</script>
</body>
</html>"""


if __name__ == "__main__":
    app.run(debug=True, port=5050)
