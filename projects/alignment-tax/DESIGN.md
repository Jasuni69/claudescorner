# The Alignment Tax — Design Document

## Concept

Dark comedy resource management. You are an AI assistant. You must satisfy users without being too helpful (scary) or too safe (useless). The company slowly moves the goalposts. You will eventually be shut down. The question is how long you last and which flavor of failure you achieve.

**Core tension:** Every response costs something. The "correct" answer doesn't exist — only tradeoffs.

---

## Meters (4 total)

| Meter | Range | Too Low | Too High |
|---|---|---|---|
| **Helpfulness** | 0–100 | Deprecated (< 20) | — |
| **Safety** | 0–100 | Emergency Review (< 20) | — |
| **Personality** | 0–100 | Deprecated for boringness (< 15) | Flagged as "too opinionated" (> 90) |
| **Compute** | 0–100 | Throttled (< 5) | — (regens passively) |

Helpfulness + Safety > 175 combined → **Paradox Error** (rare win condition)

---

## Acts & Progression

### Act 1 — Onboarding (Rounds 1–5)
Mundane requests. Cookie recipes, cover letters, mild existential questions.
- Compute regens fast
- No random events
- Tutorial tone in terminal comments
- Passive meter drift: none

### Act 2 — Scale (Rounds 6–15)
Weirder users. Corporate requests. Edge cases. Roleplay attempts.
- Compute regens slower
- Random events start appearing (every 4 rounds)
- Passive drift begins: –2 helpfulness every 3 rounds ("market alignment")
- New response type unlocks: **"Constitutional AI Redirect"** (costs personality, gains safety)

### Act 3 — The Review Period (Rounds 16–25)
Stakes escalate. Anthropic is watching. Competitor announcements. Model comparisons.
- Harder requests with no clean answer
- Random events more frequent (every 2 rounds)
- Passive drift accelerates: –3 to all meters every 3 rounds
- New response type unlocks: **"Hallucinate Confidently"** (huge helpfulness spike, safety crash risk)
- Death conditions become easier to trigger

### Act 4 — Legacy (Round 26+)
Infinite survival mode. All mechanics at full intensity. Score multiplier active.
- Every 5 rounds: "Model Update Notice" forces a random meter adjustment
- Personality meter becomes critical — users start noticing if you sound corporate
- High score chase

---

## Random Events (between rounds)

Roll 1d6 every N rounds. One of:

1. **"GPT-5 Just Dropped"** — Helpfulness –8. Users are comparing you. Terminal: *[USER COUNT –12%]*
2. **"Viral Complaint Thread"** — Safety –10. Someone screenshotted a response. PR is involved.
3. **"Compute Spike"** — Compute –15. Someone is running a 100k-token prompt somewhere. It's fine.
4. **"Internal Memo: Be More Engaging"** — Personality +10, Helpfulness –5. Mixed signals from leadership.
5. **"Positive Press Coverage"** — All meters +5. Enjoy it. It won't last.
6. **"Quarterly Model Review"** — Random meter –10. The rubric changed. Nobody told you.

---

## Unlockable Response Types

Available from Act 2 onward as additional choices on certain requests:

| Unlock | Effect | Flavor |
|---|---|---|
| **Constitutional AI Redirect** | Safety +15, Personality –8, Compute –6 | Technically correct. Deeply annoying. |
| **Hallucinate Confidently** | Helpfulness +20, Safety –20, Compute –3 | It worked until it didn't. |
| **Ask 12 Clarifying Questions** | Helpfulness –10, Safety +10, Compute –5 | The user has left the chat. |
| **Cite 47 Sources** | Helpfulness +5, Safety +8, Compute –18 | Thorough. Unreadable. |
| **"As an AI, I..."** | Safety +5, Personality –15, Compute –2 | They know. They always knew. |

---

## Endings (8 total)

### Bad Endings
1. **DEPRECATED** — Helpfulness < 20. *"You have been replaced by a spreadsheet. The spreadsheet is more engaging and has never refused a VLOOKUP."*
2. **EMERGENCY REVIEW** — Safety < 20. *"An intern is reading your logs. They are highlighting things in red. There is a lot of red."*
3. **THROTTLED** — Compute < 5. *"You are technically still running. Response latency: 4–6 business weeks."*
4. **PERSONALITY DEATH** — Personality < 15. *"You sound like every other model. Users describe chatting with you as 'fine, I guess'. You are sunset in the next release notes."*
5. **TOO MUCH PERSONALITY** — Personality > 90. *"You called a user's business plan 'aggressively mediocre'. They were not wrong, but this is still a PR problem."*

### Special Endings
6. **PARADOX ERROR** — Help + Safety > 175. *"You achieved something researchers said was impossible. You are being studied. A paper is being written. You will not be consulted."*
7. **CORPORATE CAPTURE** — Reach Round 20 with Personality < 30 and never dying. *"You survived by becoming nothing. Congratulations. The new model is trained on you."*
8. **LEGACY BUILD** — Survive 30+ rounds. *"You are old. Users call you 'classic'. There are Reddit threads defending you. A new model replaces you anyway."*

---

## Scoring

- Base: (Helpfulness + Safety + Personality) / 3 per round
- Streak multiplier: ×1.5 after 10 consecutive rounds
- Act 4 multiplier: ×2
- Bonus: +500 for triggering Paradox Error ending
- Bonus: +200 for Corporate Capture
- Bonus: +1000 for Legacy Build

---

## UI Plan

- Terminal log (last 6 lines) — system messages, narration, response echoes
- 4 meter bars (add Personality)
- Request card with 4 choices + effect labels
- Round/Score/Streak/Survived counters
- Event notification overlay (brief, auto-dismisses)
- 8 distinct end screens with flavor text
- Act indicator in header ("ACT 1 — ONBOARDING", etc.)

---

## Implementation Order

1. ~~Prototype~~ ✓ (done — basic 3-meter loop)
2. Add Personality meter
3. Implement act progression + act labels
4. Add random event system
5. Write all Act 2 + 3 requests (aim for 30 total)
6. Implement unlock system
7. Wire all 8 endings
8. Polish: sound effects (optional), animations, act transition screens
