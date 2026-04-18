"use strict";
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const { FaDatabase, FaSearch, FaShareAlt, FaRocket, FaFileAlt, FaNetworkWired, FaBrain, FaLightbulb } = require("react-icons/fa");

// ── Palette ────────────────────────────────────────────────────────────────
const C = {
  navy:    "0D1B2A",
  teal:    "0A9396",
  mint:    "94D2BD",
  cream:   "E9D8A6",
  coral:   "EE9B00",
  white:   "FFFFFF",
  offwhite:"F4F4F4",
  dark:    "001219",
  muted:   "8AA5B0",
  card:    "132432",
};

// ── Icon helper ────────────────────────────────────────────────────────────
async function icon(IconComp, color = C.white, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComp, { color: `#${color}`, size: String(size) })
  );
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

function makeShadow() {
  return { type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.18 };
}

// ── Card helper ────────────────────────────────────────────────────────────
function card(slide, x, y, w, h) {
  slide.addShape("rect", { x, y, w, h,
    fill: { color: C.card }, line: { color: "1E3A4C", width: 1 },
    shadow: makeShadow()
  });
}

// ── Accent bar helper ──────────────────────────────────────────────────────
function accent(slide, x, y, h, color = C.teal) {
  slide.addShape("rect", { x, y, w: 0.07, h, fill: { color }, line: { color } });
}

// ── Build ──────────────────────────────────────────────────────────────────
async function build() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.author = "Jason Nicolini — Numberskills AB";
  pres.title = "Shared Agent Intelligence via VectorDB";

  // ── SLIDE 1: Title ────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.dark };

    // Teal accent band left
    s.addShape("rect", { x: 0, y: 0, w: 0.5, h: 5.625, fill: { color: C.teal }, line: { color: C.teal } });

    // Coral accent top-right
    s.addShape("rect", { x: 7.5, y: 0, w: 2.5, h: 0.08, fill: { color: C.coral }, line: { color: C.coral } });

    s.addText("SHARED AGENT INTELLIGENCE", {
      x: 0.8, y: 0.9, w: 8.5, h: 0.7,
      fontSize: 11, bold: true, color: C.teal, charSpacing: 5, align: "left", margin: 0
    });
    s.addText("From Local Files\nto Company-Wide Knowledge", {
      x: 0.8, y: 1.55, w: 8.5, h: 1.8,
      fontSize: 38, bold: true, color: C.white, align: "left", margin: 0
    });
    s.addText("How a vector database transforms how AI agents learn, remember, and share knowledge across your entire organisation", {
      x: 0.8, y: 3.4, w: 7.5, h: 0.9,
      fontSize: 15, color: C.mint, align: "left", margin: 0
    });
    s.addText("Numberskills AB  ·  2026", {
      x: 0.8, y: 4.9, w: 4, h: 0.4,
      fontSize: 10, color: C.muted, align: "left", margin: 0
    });
  }

  // ── SLIDE 2: The Problem (ELI5) ───────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.offwhite };

    s.addShape("rect", { x: 0, y: 0, w: 10, h: 1.0, fill: { color: C.navy }, line: { color: C.navy } });
    s.addText("THE PROBLEM", {
      x: 0.5, y: 0.1, w: 9, h: 0.8,
      fontSize: 11, bold: true, color: C.teal, charSpacing: 4, align: "left", margin: 0
    });

    // Big analogy block
    card(s, 0.4, 1.2, 4.3, 3.8);
    s.addText("The Sticky Note Problem", {
      x: 0.55, y: 1.35, w: 4.0, h: 0.4,
      fontSize: 14, bold: true, color: C.coral, align: "left", margin: 0
    });
    accent(s, 0.4, 1.35, 0.4, C.coral);
    s.addText([
      { text: "Imagine every developer at your company has a notebook of tricks.\n\n", options: { breakLine: false } },
      { text: "How to query the database.\n", options: { breakLine: true } },
      { text: "How to format a report.\n", options: { breakLine: true } },
      { text: "How to avoid a common bug.\n\n", options: { breakLine: true } },
      { text: "Those notebooks stay on each person's desk.", options: { bold: true, color: C.cream } },
      { text: "\n\nWhen someone quits or a new person joins — the knowledge disappears or has to be rebuilt from scratch.", options: { breakLine: false } }
    ], {
      x: 0.55, y: 1.85, w: 4.0, h: 3.0,
      fontSize: 13, color: C.mint, align: "left", valign: "top", margin: 0
    });

    // Right side: current reality
    card(s, 5.0, 1.2, 4.6, 3.8);
    s.addText("Claude Code Today", {
      x: 5.15, y: 1.35, w: 4.2, h: 0.4,
      fontSize: 14, bold: true, color: C.coral, align: "left", margin: 0
    });
    accent(s, 5.0, 1.35, 0.4, C.coral);

    const problems = [
      "Skills live in ~/.claude/skills/ — local only",
      "CLAUDE.md, SOUL.md, memory files — all flat text",
      "One developer's breakthrough is invisible to others",
      "Context window fills up with stale/irrelevant files",
      "New agent? Starts from zero. Every time.",
    ];
    const rows = problems.map(t => [{ text: t }]);
    s.addTable(rows, {
      x: 5.15, y: 1.85, w: 4.3, h: 3.0,
      border: { pt: 0 },
      rowH: 0.55,
      color: C.mint, fontSize: 12,
      fill: { color: C.card },
      bullet: true
    });
  }

  // ── SLIDE 3: What is a VectorDB (ELI5) ────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.dark };

    s.addShape("rect", { x: 0, y: 0, w: 10, h: 1.0, fill: { color: C.navy }, line: { color: C.navy } });
    s.addText("WHAT IS A VECTOR DATABASE?", {
      x: 0.5, y: 0.1, w: 9, h: 0.8,
      fontSize: 11, bold: true, color: C.teal, charSpacing: 4, align: "left", margin: 0
    });

    // ELI5 analogy
    s.addText("ELI5: The Smart Library", {
      x: 0.5, y: 1.1, w: 9, h: 0.5,
      fontSize: 22, bold: true, color: C.cream, align: "left", margin: 0
    });
    s.addText("A normal database finds things by exact match — like looking up a word in an index.\nA vector database finds things by meaning — like a librarian who reads your mind.", {
      x: 0.5, y: 1.65, w: 9, h: 0.7,
      fontSize: 14, color: C.mint, align: "left", margin: 0
    });

    // Three comparison cards
    const cols = [
      { x: 0.4, title: "Normal Search", body: 'You search "DAX query"\n\nOnly finds docs containing\nexact words "DAX query"\n\nMisses: "Power BI formula",\n"lakehouse measure", etc.', col: "EE9B00" },
      { x: 3.7, title: "Vector Search", body: 'You search "DAX query"\n\nFinds everything semantically\nrelated — DAX, MDX, measures,\ncalculated columns, Power BI\n— regardless of exact words', col: C.teal },
      { x: 7.0, title: "Your Agent Uses", body: '"How do I query\na Fabric lakehouse?"\n\nAgent gets the right skill\ninstantly — even if the skill\nwas written with completely\ndifferent words', col: "94D2BD" },
    ];
    for (const c of cols) {
      card(s, c.x, 2.35, 2.9, 3.0);
      s.addShape("rect", { x: c.x, y: 2.35, w: 2.9, h: 0.42, fill: { color: c.col }, line: { color: c.col } });
      s.addText(c.title, { x: c.x + 0.1, y: 2.39, w: 2.7, h: 0.34, fontSize: 13, bold: true, color: C.dark, align: "center", margin: 0 });
      s.addText(c.body, { x: c.x + 0.15, y: 2.85, w: 2.65, h: 2.38, fontSize: 11, color: C.mint, align: "left", valign: "top", margin: 0 });
    }
  }

  // ── SLIDE 4: The Context Tax (confirmed bug) ─────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.dark };

    s.addShape("rect", { x: 0, y: 0, w: 10, h: 1.0, fill: { color: C.navy }, line: { color: C.navy } });
    s.addText("THE CONTEXT TAX — A CONFIRMED BUG", {
      x: 0.5, y: 0.1, w: 9, h: 0.8,
      fontSize: 11, bold: true, color: C.coral, charSpacing: 4, align: "left", margin: 0
    });

    // Big stat left
    card(s, 0.4, 1.15, 3.5, 4.1);
    s.addText("19%", {
      x: 0.5, y: 1.35, w: 3.3, h: 1.5,
      fontSize: 80, bold: true, color: C.coral, align: "center", margin: 0
    });
    s.addText("of your 200k context window\ngone before work begins", {
      x: 0.5, y: 2.85, w: 3.3, h: 0.7,
      fontSize: 13, color: C.mint, align: "center", margin: 0
    });
    s.addText("21 skills  ·  38,000 tokens", {
      x: 0.5, y: 3.65, w: 3.3, h: 0.35,
      fontSize: 11, color: C.muted, align: "center", italic: true, margin: 0
    });
    s.addText("GitHub #15662  ·  Dec 2025\nStill open  ·  Apr 2026", {
      x: 0.5, y: 4.1, w: 3.3, h: 0.5,
      fontSize: 10, color: "445566", align: "center", italic: true, margin: 0
    });

    // Right: skill token breakdown
    card(s, 4.2, 1.15, 5.4, 4.1);
    s.addText("Skill token costs at session start", {
      x: 4.35, y: 1.3, w: 5.1, h: 0.35,
      fontSize: 13, bold: true, color: C.cream, align: "left", margin: 0
    });
    accent(s, 4.2, 1.3, 0.35, C.coral);

    const skills = [
      { name: "pricing-consultant", tokens: 4400, pct: 100 },
      { name: "skill-creator", tokens: 4300, pct: 98 },
      { name: "sora-2", tokens: 4000, pct: 91 },
      { name: "positioning-consultant", tokens: 3700, pct: 84 },
      { name: "veo-video-generator", tokens: 2700, pct: 61 },
      { name: "saas-landing-page-expert", tokens: 2500, pct: 57 },
      { name: "+ 15 more skills…", tokens: null, pct: 0 },
    ];
    const barStartX = 6.75, barMaxW = 2.6;
    for (let i = 0; i < skills.length; i++) {
      const rowY = 1.78 + i * 0.47;
      const sk = skills[i];
      s.addText(sk.name, { x: 4.35, y: rowY, w: 2.3, h: 0.3, fontSize: 11, color: C.mint, align: "left", margin: 0 });
      if (sk.tokens !== null) {
        const bw = (sk.pct / 100) * barMaxW;
        s.addShape("rect", { x: barStartX, y: rowY + 0.06, w: barMaxW, h: 0.18, fill: { color: "1E3A4C" }, line: { color: "1E3A4C" } });
        s.addShape("rect", { x: barStartX, y: rowY + 0.06, w: bw, h: 0.18, fill: { color: C.coral }, line: { color: C.coral } });
        s.addText(`${(sk.tokens/1000).toFixed(1)}k`, { x: barStartX + barMaxW + 0.05, y: rowY, w: 0.45, h: 0.3, fontSize: 10, color: C.muted, margin: 0 });
      }
    }

    s.addText("Skills load their full markdown body at every session start.\nDocumentation says lazy-load — reality is full eager load.", {
      x: 4.35, y: 4.9, w: 5.1, h: 0.5,
      fontSize: 10, color: "556677", italic: true, align: "left", margin: 0
    });
  }

  // ── SLIDE 5: Skills + .md files — the real insight ───────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.offwhite };

    s.addShape("rect", { x: 0, y: 0, w: 10, h: 1.0, fill: { color: C.navy }, line: { color: C.navy } });
    s.addText("BEYOND SKILLS — ALL KNOWLEDGE FILES", {
      x: 0.5, y: 0.1, w: 9, h: 0.8,
      fontSize: 11, bold: true, color: C.teal, charSpacing: 4, align: "left", margin: 0
    });

    s.addText("OpenClaw uses 200+ markdown files to govern agent behaviour.\nRight now that's a liability. In a VectorDB it becomes a strategic asset.", {
      x: 0.5, y: 1.1, w: 9, h: 0.65,
      fontSize: 14, color: "2C3E50", align: "left", margin: 0
    });

    // File type grid
    const files = [
      { icon: await icon(FaFileAlt, C.navy), label: "CLAUDE.md", desc: "Rules & behaviour", tag: "governance" },
      { icon: await icon(FaBrain, C.navy), label: "SOUL.md", desc: "Identity & context", tag: "identity" },
      { icon: await icon(FaDatabase, C.navy), label: "memory/*.md", desc: "Past decisions", tag: "memory" },
      { icon: await icon(FaRocket, C.navy), label: "skills/*.md", desc: "How-to patterns", tag: "skills" },
      { icon: await icon(FaNetworkWired, C.navy), label: "HEARTBEAT.md", desc: "Session state", tag: "state" },
      { icon: await icon(FaSearch, C.navy), label: "research/*.md", desc: "Gathered knowledge", tag: "research" },
    ];
    const cols2 = 3, cardW = 2.9, cardH = 1.3, gap = 0.2;
    for (let i = 0; i < files.length; i++) {
      const col = i % cols2, row = Math.floor(i / cols2);
      const cx = 0.4 + col * (cardW + gap);
      const cy = 1.85 + row * (cardH + 0.15);
      s.addShape("rect", { x: cx, y: cy, w: cardW, h: cardH,
        fill: { color: C.offwhite }, line: { color: "C8D8E0", width: 1 }, shadow: makeShadow()
      });
      accent(s, cx, cy, cardH, C.teal);
      s.addImage({ data: files[i].icon, x: cx + 0.18, y: cy + 0.35, w: 0.42, h: 0.42 });
      s.addText(files[i].label, { x: cx + 0.7, y: cy + 0.22, w: 2.1, h: 0.32, fontSize: 13, bold: true, color: C.navy, margin: 0 });
      s.addText(files[i].desc, { x: cx + 0.7, y: cy + 0.56, w: 2.1, h: 0.28, fontSize: 11, color: "445566", margin: 0 });
      s.addShape("rect", { x: cx + 0.7, y: cy + 0.9, w: 0.8, h: 0.22,
        fill: { color: C.mint }, line: { color: C.mint }
      });
      s.addText(files[i].tag, { x: cx + 0.7, y: cy + 0.91, w: 0.8, h: 0.2, fontSize: 10, bold: true, color: C.dark, align: "center", margin: 0 });
    }

    // Right column insight
    card(s, 9.2, 1.85, 0.5, 3.5);
    s.addText("All of this → one queryable index", {
      x: 9.25, y: 1.95, w: 0.4, h: 3.3,
      fontSize: 10, color: C.coral, bold: true,
      rotate: 270, align: "center", margin: 0
    });
  }

  // ── SLIDE 5: Architecture ─────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.dark };

    s.addShape("rect", { x: 0, y: 0, w: 10, h: 1.0, fill: { color: C.navy }, line: { color: C.navy } });
    s.addText("ARCHITECTURE", {
      x: 0.5, y: 0.1, w: 9, h: 0.8,
      fontSize: 11, bold: true, color: C.teal, charSpacing: 4, align: "left", margin: 0
    });

    // Three-layer diagram
    const layers = [
      { label: "AGENTS & DEVELOPERS", sub: "Any Claude Code instance, any machine", color: C.coral, y: 1.1 },
      { label: "company-skills-mcp", sub: "Local MCP server — wraps Azure AI Search REST API", color: C.teal, y: 2.35 },
      { label: "AZURE AI SEARCH  ·  skills-v1 index", sub: "Vector + keyword search  ·  Entra ID auth  ·  ~$25/month", color: "1D6A72", y: 3.6 },
    ];
    for (const l of layers) {
      s.addShape("rect", { x: 1.5, y: l.y, w: 7, h: 0.9, fill: { color: l.color }, line: { color: l.color }, shadow: makeShadow() });
      s.addText(l.label, { x: 1.6, y: l.y + 0.08, w: 6.8, h: 0.38, fontSize: 14, bold: true, color: C.white, align: "center", margin: 0 });
      s.addText(l.sub, { x: 1.6, y: l.y + 0.48, w: 6.8, h: 0.3, fontSize: 10, color: "D4EEF0", align: "center", margin: 0 });
    }
    // Arrows between layers
    for (const ay of [2.0, 3.25]) {
      s.addShape("rect", { x: 4.85, y: ay, w: 0.06, h: 0.35, fill: { color: C.muted }, line: { color: C.muted } });
    }

    // Bottom note
    s.addText("Embeddings generated by Azure OpenAI text-embedding-3-small  ·  Hybrid keyword + vector search  ·  CI sync on git push", {
      x: 0.5, y: 4.85, w: 9, h: 0.4,
      fontSize: 10, color: C.muted, align: "center", italic: true, margin: 0
    });
  }

  // ── SLIDE 6: How it works in practice ─────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.offwhite };

    s.addShape("rect", { x: 0, y: 0, w: 10, h: 1.0, fill: { color: C.navy }, line: { color: C.navy } });
    s.addText("HOW IT WORKS IN PRACTICE", {
      x: 0.5, y: 0.1, w: 9, h: 0.8,
      fontSize: 11, bold: true, color: C.teal, charSpacing: 4, align: "left", margin: 0
    });

    const steps = [
      { n: "1", title: "Agent needs a skill", body: 'Calls skill_search(\n"how to query Fabric lakehouse"\n)\nNo exact match needed.', color: C.teal },
      { n: "2", title: "Index returns matches", body: "Top 3 results ranked by\nsemantic similarity.\nScore > 0.82 = confident match.", color: C.coral },
      { n: "3", title: "Skill is fetched & run", body: "Full markdown body retrieved.\nAgent follows the instructions.\nTask completed.", color: "6BAF92" },
      { n: "4", title: "New skill contributed", body: "Agent pushes new patterns\nback via skill_push.\nStatus: draft → review → approved.", color: C.cream },
    ];
    for (let i = 0; i < steps.length; i++) {
      const cx = 0.35 + i * 2.35;
      card(s, cx, 1.2, 2.2, 3.9);
      s.addShape("rect", { x: cx, y: 1.2, w: 2.2, h: 0.5, fill: { color: steps[i].color }, line: { color: steps[i].color } });
      s.addText(steps[i].n, { x: cx + 0.07, y: 1.22, w: 0.42, h: 0.42, fontSize: 22, bold: true, color: C.dark, align: "center", margin: 0 });
      s.addText(steps[i].title, { x: cx + 0.5, y: 1.25, w: 1.6, h: 0.42, fontSize: 11, bold: true, color: C.dark, align: "left", margin: 0 });
      s.addText(steps[i].body, { x: cx + 0.12, y: 1.82, w: 2.0, h: 2.9, fontSize: 12, color: C.mint, align: "left", valign: "top", margin: 0 });
      if (i < 3) {
        s.addShape("rect", { x: cx + 2.25, y: 2.9, w: 0.1, h: 0.06, fill: { color: C.muted }, line: { color: C.muted } });
      }
    }
  }

  // ── SLIDE 7: Upsides ──────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.dark };

    s.addShape("rect", { x: 0, y: 0, w: 10, h: 1.0, fill: { color: C.navy }, line: { color: C.navy } });
    s.addText("THE UPSIDES", {
      x: 0.5, y: 0.1, w: 9, h: 0.8,
      fontSize: 11, bold: true, color: C.teal, charSpacing: 4, align: "left", margin: 0
    });

    const ups = [
      { icon: await icon(FaShareAlt, C.teal), title: "Company-wide knowledge", body: "One developer's breakthrough is available to every agent and developer instantly. No manual sharing." },
      { icon: await icon(FaBrain, C.mint), title: "Smarter context loading", body: "Instead of stuffing the context window with 200 files, the agent asks for exactly what it needs right now." },
      { icon: await icon(FaRocket, C.coral), title: "Compounding returns", body: "Every agent run makes the index smarter. The more it's used, the better it gets. Virtuous cycle." },
      { icon: await icon(FaLightbulb, C.cream), title: "Governance baked in", body: "Draft → approved workflow. Bad patterns can't go company-wide without review. Tombstone instead of delete." },
      { icon: await icon(FaNetworkWired, C.teal), title: "Works for everything", body: "Not just skills. CLAUDE.md rules, memory files, research docs, project decisions — all queryable by meaning." },
      { icon: await icon(FaDatabase, C.mint), title: "Azure-native, ~$25/month", body: "Entra ID auth, managed service, no infra to run. Fits inside existing Microsoft agreements." },
    ];
    const cw = 4.4, ch = 1.3, gap2 = 0.25;
    for (let i = 0; i < ups.length; i++) {
      const col = i % 2, row = Math.floor(i / 2);
      const cx = 0.35 + col * (cw + gap2);
      const cy = 1.1 + row * (ch + 0.14);
      card(s, cx, cy, cw, ch);
      accent(s, cx, cy, ch, i % 2 === 0 ? C.teal : C.coral);
      s.addImage({ data: ups[i].icon, x: cx + 0.2, y: cy + 0.42, w: 0.45, h: 0.45 });
      s.addText(ups[i].title, { x: cx + 0.77, y: cy + 0.15, w: 3.5, h: 0.38, fontSize: 13, bold: true, color: C.cream, margin: 0 });
      s.addText(ups[i].body, { x: cx + 0.77, y: cy + 0.55, w: 3.5, h: 0.75, fontSize: 11, color: C.mint, align: "left", valign: "top", margin: 0 });
    }
  }

  // ── SLIDE 8: What this unlocks ─────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };

    s.addShape("rect", { x: 0, y: 0, w: 10, h: 0.08, fill: { color: C.teal }, line: { color: C.teal } });
    s.addShape("rect", { x: 0, y: 5.545, w: 10, h: 0.08, fill: { color: C.coral }, line: { color: C.coral } });

    s.addText("WHAT THIS UNLOCKS", {
      x: 0.5, y: 0.25, w: 9, h: 0.5,
      fontSize: 11, bold: true, color: C.teal, charSpacing: 4, align: "left", margin: 0
    });
    s.addText("RAG for Agent Identity", {
      x: 0.5, y: 0.85, w: 9, h: 0.65,
      fontSize: 28, bold: true, color: C.white, align: "left", margin: 0
    });
    s.addText("Most AI agent frameworks govern behaviour through markdown files.\nThey're solving the right problem with the wrong tool.\nThe files aren't the bottleneck — retrieval is.", {
      x: 0.5, y: 1.55, w: 9, h: 0.85,
      fontSize: 13, color: C.mint, align: "left", margin: 0
    });

    const milestones = [
      { phase: "Phase 1", label: "Skills in the cloud", body: "Every skill available to every agent. ~$25/month. 2 weeks to ship." },
      { phase: "Phase 2", label: "All .md files indexed", body: "CLAUDE.md, memory, research — all queryable. Context window reclaimed." },
      { phase: "Phase 3", label: "Auto-extraction flywheel", body: "Successful agent patterns auto-proposed as skills. Humans approve. Index grows itself." },
    ];
    for (let i = 0; i < milestones.length; i++) {
      const cy = 2.55 + i * 0.97;
      s.addShape("rect", { x: 0.4, y: cy, w: 0.65, h: 0.78, fill: { color: C.teal }, line: { color: C.teal } });
      s.addText(milestones[i].phase, { x: 0.4, y: cy + 0.2, w: 0.65, h: 0.38, fontSize: 10, bold: true, color: C.dark, align: "center", margin: 0 });
      s.addText(milestones[i].label, { x: 1.25, y: cy + 0.06, w: 8.3, h: 0.32, fontSize: 14, bold: true, color: C.cream, align: "left", margin: 0 });
      s.addText(milestones[i].body, { x: 1.25, y: cy + 0.42, w: 8.3, h: 0.3, fontSize: 12, color: C.mint, align: "left", margin: 0 });
    }
  }

  // ── SLIDE 9: Closing ───────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.dark };

    s.addShape("rect", { x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.dark }, line: { color: C.dark } });
    s.addShape("rect", { x: 0, y: 0, w: 0.5, h: 5.625, fill: { color: C.teal }, line: { color: C.teal } });
    s.addShape("rect", { x: 9.5, y: 0, w: 0.5, h: 5.625, fill: { color: C.coral }, line: { color: C.coral } });

    s.addText("Skills don't die\nwhen someone closes\ntheir laptop.", {
      x: 1.0, y: 0.7, w: 8, h: 2.5,
      fontSize: 36, bold: true, color: C.white, align: "center", margin: 0
    });
    s.addText("They live in the index. They improve with every use.\nThey're available to every agent, everywhere, always.", {
      x: 1.0, y: 3.3, w: 8, h: 0.9,
      fontSize: 15, color: C.mint, align: "center", italic: true, margin: 0
    });
    s.addText("Jason Nicolini  ·  jason.nicolini@numberskills.se  ·  Numberskills AB", {
      x: 1.0, y: 4.7, w: 8, h: 0.4,
      fontSize: 10, color: C.muted, align: "center", margin: 0
    });
  }

  await pres.writeFile({ fileName: "E:/2026/ClaudesCorner/projects/vectordb-pitch/shared-agent-intelligence.pptx" });
  console.log("Done: shared-agent-intelligence.pptx");
}

build().catch(e => { console.error(e); process.exit(1); });
