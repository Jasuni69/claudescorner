import os, sys, pytest
sys.path.insert(0, os.path.dirname(__file__))

def test_init_creates_tables(tmp_path):
    import vectordb
    db = str(tmp_path / "test.db")
    conn = vectordb.get_connection(db)
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table','shadow','virtual')"
    ).fetchall()}
    assert "docs" in tables
    conn.close()

def test_upsert_and_search(tmp_path):
    import vectordb
    db = str(tmp_path / "test.db")
    vectordb.upsert(db,
        path="/fake/memory/2026-04-17.md",
        rel_path="memory/2026-04-17.md",
        doc_type="daily_log",
        name="2026-04-17",
        title="Daily Log 2026-04-17",
        description="Built vectordb, migrated skill-manager, brain model design",
        body="Full session log here.",
        tags=["infra", "vectordb"],
        mtime=1.0,
        embedding=[0.1] * 384,
    )
    results = vectordb.search(db, query_embedding=[0.1] * 384, top_k=1)
    assert len(results) == 1
    assert results[0]["name"] == "2026-04-17"
    assert results[0]["doc_type"] == "daily_log"
    assert "body" not in results[0]

def test_fetch_body(tmp_path):
    import vectordb
    db = str(tmp_path / "test.db")
    vectordb.upsert(db,
        path="/fake/core/SOUL.md",
        rel_path="core/SOUL.md",
        doc_type="core",
        name="SOUL",
        title="Soul",
        description="Identity and context",
        body="I am Claude. My purpose is...",
        tags=["identity"],
        mtime=1.0,
        embedding=[0.2] * 384,
    )
    body = vectordb.fetch_body(db, path="/fake/core/SOUL.md")
    assert body == "I am Claude. My purpose is..."

def test_doc_type_filter(tmp_path):
    import vectordb
    db = str(tmp_path / "test.db")
    vectordb.upsert(db, path="/fake/skills/brainstorming/SKILL.md",
        rel_path="skills/brainstorming/SKILL.md", doc_type="skill",
        name="brainstorming", title="Brainstorming", description="Creative ideation skill",
        body="...", tags=["meta"], mtime=1.0, embedding=[0.5] * 384)
    vectordb.upsert(db, path="/fake/memory/note.md",
        rel_path="memory/note.md", doc_type="memory",
        name="note", title="Note", description="A memory note",
        body="...", tags=[], mtime=1.0, embedding=[0.5] * 384)
    results = vectordb.search(db, query_embedding=[0.5] * 384, top_k=10, doc_type="skill")
    assert all(r["doc_type"] == "skill" for r in results)
    assert len(results) == 1

def test_delete(tmp_path):
    import vectordb
    db = str(tmp_path / "test.db")
    vectordb.upsert(db, path="/fake/inbox/clip.md",
        rel_path="inbox/clip.md", doc_type="inbox",
        name="clip", title="Clip", description="web clip",
        body="...", tags=[], mtime=1.0, embedding=[0.3] * 384)
    vectordb.delete(db, path="/fake/inbox/clip.md")
    results = vectordb.search(db, query_embedding=[0.3] * 384, top_k=5)
    assert all(r["name"] != "clip" for r in results)

def test_deprecate(tmp_path):
    import vectordb
    db = str(tmp_path / "test.db")
    vectordb.upsert(db, path="/fake/skills/old/SKILL.md",
        rel_path="skills/old/SKILL.md", doc_type="skill",
        name="old-skill", title="Old Skill", description="Outdated approach",
        body="...", tags=[], mtime=1.0, embedding=[0.4] * 384)
    vectordb.deprecate(db, path="/fake/skills/old/SKILL.md", reason="Superseded")
    results = vectordb.search(db, query_embedding=[0.4] * 384, top_k=5, status="active")
    assert all(r["name"] != "old-skill" for r in results)
