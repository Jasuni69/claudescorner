#!/usr/bin/env python3
"""
consolidate.py — promote repeated facts from daily_logs into durable memory/.

Brain analogue: hippocampal episodic traces that keep recurring get replayed
into neocortical semantic memory. Here: scan recent daily_logs, find clusters
of similar chunks that appear across multiple days, and emit a candidate
memory file under `memory/consolidated/<slug>.md` for Claude to review.

No LLM call required — this does recall (retrieval + clustering) and proposes;
the writing step is intentionally left to an interactive turn so we don't
silently fabricate memories.

Usage:
  python consolidate.py                  # dry-run, show candidates
  python consolidate.py --window-days 30 # look back further
  python consolidate.py --min-cluster 3  # tighter threshold
  python consolidate.py --write          # emit .md proposals (review before committing)
"""
import argparse
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SRC = Path(__file__).parent
sys.path.insert(0, str(SRC))

import vectordb

BASE = Path(__file__).parent.parent.parent.parent
MEMORY_DIR = BASE / "memory"
CONSOLIDATED_DIR = MEMORY_DIR / "consolidated"

# Clustering thresholds
COSINE_MERGE = 0.78          # two chunks this close → same cluster
MIN_CLUSTER_SIZE = 2         # minimum number of distinct daily_logs in a cluster
MAX_WINDOW_DAYS = 60


def _fetch_episodic_chunks(window_days: int) -> list[dict]:
    """Return chunks from daily_log / journal docs within the window."""
    import numpy as np
    conn = vectordb.get_connection()
    now_ts = datetime.now(timezone.utc).timestamp()
    cutoff = now_ts - (window_days * 86400)
    rows = conn.execute("""
        SELECT c.id AS chunk_id, c.doc_id, c.section, c.text,
               d.doc_type, d.name, d.path, d.mtime, v.embedding
        FROM doc_chunks c
        JOIN docs d       ON d.id = c.doc_id
        JOIN vec_docs v   ON v.id = c.id
        WHERE d.doc_type IN ('daily_log', 'journal')
          AND d.mtime >= ?
          AND d.status = 'active'
    """, (cutoff,)).fetchall()
    out = []
    for r in rows:
        vec = np.frombuffer(r["embedding"], dtype="float32")
        vec = vec / (max(float((vec ** 2).sum()) ** 0.5, 1e-9))
        out.append({
            "chunk_id": r["chunk_id"],
            "doc_id": r["doc_id"],
            "doc_name": r["name"],
            "section": r["section"],
            "text": r["text"],
            "vec": vec,
        })
    return out


def _cluster(chunks: list[dict], threshold: float) -> list[list[int]]:
    """Greedy agglomerative clustering by cosine."""
    import numpy as np
    if not chunks:
        return []
    vecs = np.stack([c["vec"] for c in chunks])
    sim = vecs @ vecs.T
    n = len(chunks)
    assigned = [-1] * n
    clusters: list[list[int]] = []
    for i in range(n):
        if assigned[i] != -1:
            continue
        group = [i]
        assigned[i] = len(clusters)
        for j in range(i + 1, n):
            if assigned[j] == -1 and sim[i, j] >= threshold:
                group.append(j)
                assigned[j] = len(clusters)
        clusters.append(group)
    return clusters


def _slugify(text: str, maxlen: int = 50) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (slug[:maxlen] or "cluster").rstrip("-")


def _cluster_title(chunks: list[dict]) -> str:
    # Prefer section heading if most chunks share one; else first line of largest chunk.
    sections = [c["section"] for c in chunks if c["section"]]
    if sections:
        # pick mode
        counts: dict[str, int] = {}
        for s in sections:
            counts[s] = counts.get(s, 0) + 1
        top = max(counts.items(), key=lambda kv: kv[1])
        if top[1] >= max(2, len(chunks) // 2):
            return top[0]
    longest = max(chunks, key=lambda c: len(c["text"]))
    first_line = longest["text"].strip().splitlines()[0] if longest["text"].strip() else "cluster"
    return first_line[:80].lstrip("# ").strip()


def _render_proposal(cluster_chunks: list[dict], title: str) -> str:
    doc_names = sorted({c["doc_name"] for c in cluster_chunks})
    now = datetime.now().strftime("%Y-%m-%d")
    body = [
        f"---",
        f"title: {title}",
        f"type: consolidated",
        f"sources: {', '.join(doc_names)}",
        f"generated: {now}",
        f"---",
        "",
        f"# {title}",
        "",
        f"Consolidated from {len(doc_names)} daily log(s): {', '.join(doc_names)}.",
        "",
        "## Source excerpts",
        "",
    ]
    for c in cluster_chunks:
        body.append(f"### {c['doc_name']}" + (f" § {c['section']}" if c["section"] else ""))
        body.append("")
        body.append(c["text"].strip())
        body.append("")
    body += [
        "## Proposed durable fact",
        "",
        "_Edit the summary above, remove source excerpts, and move this file to "
        "`memory/` as a named memory entry once validated._",
        "",
    ]
    return "\n".join(body)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window-days", type=int, default=30)
    ap.add_argument("--min-cluster", type=int, default=MIN_CLUSTER_SIZE)
    ap.add_argument("--threshold", type=float, default=COSINE_MERGE)
    ap.add_argument("--write", action="store_true",
                    help="Emit proposal files under memory/consolidated/")
    args = ap.parse_args()

    if args.window_days > MAX_WINDOW_DAYS:
        print(f"clamping window to {MAX_WINDOW_DAYS}d")
        args.window_days = MAX_WINDOW_DAYS

    chunks = _fetch_episodic_chunks(args.window_days)
    print(f"Fetched {len(chunks)} chunks from episodic docs in last {args.window_days}d")
    if not chunks:
        return 0

    clusters = _cluster(chunks, args.threshold)
    candidates = []
    for cl in clusters:
        members = [chunks[i] for i in cl]
        distinct_docs = {m["doc_id"] for m in members}
        if len(distinct_docs) < args.min_cluster:
            continue
        candidates.append(members)

    print(f"\nFound {len(candidates)} candidate cluster(s) "
          f"(>= {args.min_cluster} distinct docs, cosine >= {args.threshold})")

    if not candidates:
        return 0

    if args.write:
        CONSOLIDATED_DIR.mkdir(exist_ok=True, parents=True)

    for i, members in enumerate(candidates, 1):
        title = _cluster_title(members)
        slug = _slugify(title)
        print(f"\n[{i}] {title}  (spans {len({m['doc_name'] for m in members})} logs, "
              f"{len(members)} chunks)")
        for m in members[:3]:
            preview = m["text"].strip().replace("\n", " ")[:110]
            print(f"    - {m['doc_name']}: {preview}")
        if args.write:
            fname = CONSOLIDATED_DIR / f"{slug}-{hashlib.sha1(title.encode()).hexdigest()[:6]}.md"
            fname.write_text(_render_proposal(members, title), encoding="utf-8")
            print(f"    -> wrote {fname.relative_to(BASE)}")

    if not args.write:
        print("\n(dry-run — re-run with --write to emit proposal files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
