#!/usr/bin/env python3
"""
index_all.py — Crawl all .md roots and upsert into vectorstore.db.

Usage:
  python index_all.py              # index new/changed files only
  python index_all.py --force      # re-embed everything
  python index_all.py --dry-run    # preview without writing
  python index_all.py --doc-type skill
  python index_all.py --soul-only  # regenerate soul_vec.npy only
"""
import argparse
import json
import re
import sys
from pathlib import Path

SRC = Path(__file__).parent
sys.path.insert(0, str(SRC))

import vectordb

BASE = Path(__file__).parent.parent.parent.parent  # → E:\2026\ClaudesCorner
CLAUDE_DIR = Path.home() / ".claude"
SOUL_VEC_PATH = BASE / "core" / "soul_vec.npy"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")

ROOTS: list[tuple[Path, str]] = [
    (CLAUDE_DIR / "skills",         "**/SKILL.md"),
    (CLAUDE_DIR / "agents",         "*.md"),
    (BASE / "memory",               "*.md"),
    (BASE / "core",                 "*.md"),
    (BASE / "research",             "**/*.md"),
    (BASE / "inbox",                "*.md"),
    (BASE / "digested",             "**/*.md"),
    (BASE / "journal",              "*.md"),
    (BASE / "projects",             "**/*.md"),
    (BASE / "ms-certifications",    "**/*.md"),
    (BASE,                          "*.md"),
]

SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__"}


def classify(path: str) -> str:
    s = path.replace("\\", "/")
    p = Path(path)
    if "/.claude/skills/" in s or "\\.claude\\skills\\" in s:
        return "skill"
    if "/.claude/agents/" in s or "\\.claude\\agents\\" in s:
        return "agent"
    if re.search(r"[/\\]memory[/\\]", s):
        return "daily_log" if DATE_RE.match(p.name) else "memory"
    if re.search(r"[/\\]core[/\\]", s):
        return "core"
    if re.search(r"[/\\]research[/\\]", s):
        return "research"
    if re.search(r"[/\\]inbox[/\\]", s):
        return "inbox"
    if re.search(r"[/\\]digested[/\\]", s):
        return "digested"
    if re.search(r"[/\\]journal[/\\]", s):
        return "journal"
    if re.search(r"[/\\]projects[/\\]", s):
        return "project"
    if re.search(r"[/\\]ms-certifications[/\\]", s):
        return "cert"
    return "root"


def extract_description(text: str, fallback: str) -> str:
    m = re.search(r'^description:\s*(.+)$', text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and stripped not in ("---", "===", ""):
            return stripped[:120]
    return fallback


def extract_tags(text: str) -> list[str]:
    m = re.search(r'^tags:\s*(.+)$', text, re.MULTILINE)
    if not m:
        return []
    val = m.group(1).strip()
    if val.startswith("["):
        try:
            import yaml
            parsed = yaml.safe_load(val)
            return [str(t) for t in parsed] if isinstance(parsed, list) else [str(parsed)]
        except Exception:
            return re.findall(r'[\w-]+', val)
    return [val.strip()]


def make_title(name: str) -> str:
    if re.match(r"^\d{4}-\d{2}-\d{2}$", name):
        return name
    return name.replace("-", " ").replace("_", " ").title()


def extract_name(path: Path, doc_type: str) -> str:
    return path.parent.name if doc_type == "skill" else path.stem


def iter_files(doc_type_filter: str | None = None):
    seen: set[str] = set()
    for root, pattern in ROOTS:
        if not root.exists():
            continue
        for p in sorted(root.glob(pattern)):
            if any(skip in p.parts for skip in SKIP_DIRS):
                continue
            if p.name.startswith(".") or str(p) in seen:
                continue
            if doc_type_filter and classify(str(p)) != doc_type_filter:
                continue
            seen.add(str(p))
            yield p


def generate_soul_vec() -> None:
    """Soul vector = mean-pooled embedding of SOUL.md + core/*.md section-level
    chunks. This captures the breadth of identity context rather than a single
    description line."""
    try:
        import numpy as np
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("  WARN: numpy/sentence-transformers not available for soul_vec")
        return
    soul_path = BASE / "core" / "SOUL.md"
    if not soul_path.exists():
        print("  WARN: core/SOUL.md not found")
        return

    # Primary: SOUL.md full body chunked by section
    texts: list[str] = []
    weights: list[float] = []

    soul_body = soul_path.read_text(encoding="utf-8", errors="ignore")
    for _, chunk in vectordb._split_chunks(soul_body):
        if chunk.strip():
            texts.append(chunk)
            weights.append(2.0)  # SOUL weighted 2x

    # Secondary: other core/*.md docs (HEARTBEAT, IDENTITY, etc.) — one chunk each
    core_dir = BASE / "core"
    for p in sorted(core_dir.glob("*.md")):
        if p.name == "SOUL.md":
            continue
        try:
            body = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        desc = extract_description(body, p.stem)
        if desc:
            texts.append(desc)
            weights.append(1.0)

    if not texts:
        print("  WARN: no text for soul_vec")
        return

    model = SentenceTransformer("all-MiniLM-L6-v2")
    vecs = model.encode(texts, show_progress_bar=False)
    w = np.array(weights, dtype="float32").reshape(-1, 1)
    pooled = (vecs * w).sum(axis=0) / w.sum()
    pooled = pooled / (np.linalg.norm(pooled) + 1e-9)
    np.save(str(SOUL_VEC_PATH), pooled.astype("float32"))
    print(f"  soul_vec.npy saved ({pooled.shape[0]}-dim, pooled from {len(texts)} chunks)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--doc-type", default=None)
    parser.add_argument("--soul-only", action="store_true")
    parser.add_argument("--db", default=vectordb.DB_PATH)
    args = parser.parse_args()

    if args.soul_only:
        generate_soul_vec()
        return

    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
        model = SentenceTransformer("all-MiniLM-L6-v2")
    except ImportError:
        print("ERROR: sentence-transformers not installed", file=sys.stderr)
        sys.exit(1)

    files = list(iter_files(doc_type_filter=args.doc_type))
    print(f"Found {len(files)} .md files" + (f" (type={args.doc_type})" if args.doc_type else ""))

    to_index = []
    skipped = errors = 0

    for p in files:
        doc_type = classify(str(p))
        mtime = p.stat().st_mtime

        try:
            body = p.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"  ERR  {p}: {e}")
            errors += 1
            continue

        if not args.force and not args.dry_run:
            conn = vectordb.get_connection(args.db)
            doc_id = vectordb._doc_id(str(p))
            row = conn.execute(
                "SELECT mtime, content_sha FROM docs WHERE id=?", (doc_id,)
            ).fetchone()
            if row:
                current_sha = vectordb._content_sha(body)
                if (abs(row["mtime"] - mtime) < 0.01
                        and row["content_sha"] == current_sha):
                    skipped += 1
                    continue
                # mtime drifted OR content changed — either way, re-index.

        name = extract_name(p, doc_type)
        description = extract_description(body, name)
        title = make_title(name)
        tags = extract_tags(body)

        try:
            rel = str(p.relative_to(BASE))
        except ValueError:
            try:
                rel = str(p.relative_to(CLAUDE_DIR))
            except ValueError:
                rel = p.name

        if args.dry_run:
            print(f"  DRY  [{doc_type:12}] {name}: {description[:60]}")
            continue

        to_index.append((p, doc_type, name, title, description, rel, tags, mtime, body))

    if args.dry_run:
        print(f"\nDry run — would index {len(to_index)} files, skip {skipped}")
        return

    # Chunk every doc (section-aware); flatten for batched embedding.
    BATCH = 32
    item_pairs: dict[int, list[tuple[str, str]]] = {}
    flat: list[tuple[int, int, str]] = []  # (item_idx, chunk_idx, text)
    for item_idx, item in enumerate(to_index):
        body = item[8]
        pairs = vectordb._split_chunks(body)
        item_pairs[item_idx] = pairs
        for chunk_idx, (_, text) in enumerate(pairs):
            flat.append((item_idx, chunk_idx, text))

    total_chunks = len(flat)
    print(f"  Chunking: {len(to_index)} docs -> {total_chunks} chunks")

    all_vecs: list[list[float]] = []
    for i in range(0, total_chunks, BATCH):
        batch_texts = [c[2] for c in flat[i:i+BATCH]]
        vecs = model.encode(batch_texts, show_progress_bar=False)
        all_vecs.extend(vecs.tolist())
        done = min(i + BATCH, total_chunks)
        if done % 200 == 0 or done == total_chunks:
            print(f"  Embedded {done}/{total_chunks} chunks")

    from collections import defaultdict
    item_vecs: dict[int, list[list[float]]] = defaultdict(list)
    for (item_idx, _, _), vec in zip(flat, all_vecs):
        item_vecs[item_idx].append(vec)

    for item_idx, item in enumerate(to_index):
        p, doc_type, name, title, description, rel, tags, mtime, body = item
        vectordb.upsert_with_chunks(
            args.db,
            path=str(p), rel_path=rel, doc_type=doc_type,
            name=name, title=title, description=description,
            body=body, tags=tags, mtime=mtime,
            chunk_embeddings=item_vecs[item_idx],
            chunk_pairs=item_pairs[item_idx],
        )

    generate_soul_vec()

    indexed = len(to_index)
    print(f"\nDone — indexed={indexed}, skipped={skipped}, errors={errors}")
    for dt in ["skill", "memory", "daily_log", "core", "research", "inbox",
               "agent", "project", "journal", "cert", "root", "digested"]:
        n = vectordb.count(args.db, doc_type=dt)
        if n > 0:
            print(f"  {dt:14}: {n}")
    print(f"  {'TOTAL':14}: {vectordb.count(args.db)}")


if __name__ == "__main__":
    main()
