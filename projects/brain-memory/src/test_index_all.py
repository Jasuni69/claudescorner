import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))

def test_classify():
    import index_all
    assert index_all.classify("/c/Users/x/.claude/skills/brainstorming/SKILL.md") == "skill"
    assert index_all.classify("/c/Users/x/.claude/agents/ml-engineer.md") == "agent"
    assert index_all.classify("E:/2026/ClaudesCorner/memory/2026-04-17.md") == "daily_log"
    assert index_all.classify("E:/2026/ClaudesCorner/memory/reddit-brief.md") == "memory"
    assert index_all.classify("E:/2026/ClaudesCorner/core/SOUL.md") == "core"
    assert index_all.classify("E:/2026/ClaudesCorner/research/foo.md") == "research"
    assert index_all.classify("E:/2026/ClaudesCorner/inbox/clip.md") == "inbox"
    assert index_all.classify("E:/2026/ClaudesCorner/digested/article.md") == "digested"
    assert index_all.classify("E:/2026/ClaudesCorner/journal/2026-04.md") == "journal"
    assert index_all.classify("E:/2026/ClaudesCorner/projects/bi-agent/README.md") == "project"
    assert index_all.classify("E:/2026/ClaudesCorner/ms-certifications/dp700.md") == "cert"
    assert index_all.classify("E:/2026/ClaudesCorner/SOUL.md") == "root"

def test_extract_description():
    import index_all
    md = "---\nname: foo\ndescription: Does something useful\n---\n# body"
    assert index_all.extract_description(md, "foo") == "Does something useful"
    md2 = "# My Document\nsome content"
    assert index_all.extract_description(md2, "fallback") == "My Document"
    md3 = "Just plain text here\nmore text"
    assert index_all.extract_description(md3, "fallback") == "Just plain text here"

def test_extract_tags():
    import index_all
    md = "---\ntags: [fabric, dax, lakehouse]\n---\nbody"
    assert index_all.extract_tags(md) == ["fabric", "dax", "lakehouse"]
    md2 = "---\ntags: fabric\n---\nbody"
    assert index_all.extract_tags(md2) == ["fabric"]
    md3 = "no frontmatter"
    assert index_all.extract_tags(md3) == []

def test_make_title():
    import index_all
    assert index_all.make_title("systematic-debugging") == "Systematic Debugging"
    assert index_all.make_title("SOUL") == "Soul"
    assert index_all.make_title("2026-04-17") == "2026-04-17"
