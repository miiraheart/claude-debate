# Product Mode Execution

Product mode runs six sequential phases. Each phase has a clear gate before proceeding.

---

## Phase 1 — Research Sprint

**Goal:** Each agent researches products in the space and documents candidates with URLs.

Send research task to ALL agents in parallel:

```
For each agent-N:
SendMessage(
  type: "message",
  recipient: "agent-<N>",
  summary: "Phase 1: Research sprint",
  content: """
PHASE 1 — RESEARCH SPRINT

Topic: <TOPIC>
Your persona: <PERSONA_NAME> — <PERSONA_DESCRIPTION>

Research products that address this topic. For each candidate:
- Product name and URL
- Key differentiators
- Price range
- Best suited for (user type)
- One-line verdict from your persona's perspective

Write your research to: /tmp/debate-session/phase1/agent-<N>.md

Aim for 5-8 candidates. Prefer products with verifiable public URLs.
"""
)
```

After all agents respond, run:

```bash
python3 scripts/debate_orchestrator.py summarize-research
```

**URL verification:** For each product URL extracted by the script, call `WebFetch` to confirm the URL resolves and the page is a real product. Mark unverified products.

```bash
python3 scripts/debate_orchestrator.py update-state '{"verified": [...], "unverified": [...]}'
```

**User gate:** Report to the user:
- Verified products (with names and URLs)
- Unverified products (excluded)
- Ask to proceed to Phase 2

Log:

```bash
echo "[$(date '+%H:%M:%S')] PHASE1 — Research complete. Verified: <N> products. Awaiting user confirmation." >> debate-output/debate.log
```

---

## Phase 2 — Opening Statements

**Goal:** Each agent declares their single top pick. No duplicates allowed.

Run sequentially — each agent sees what previous agents picked.

**First speaker (agent-1):**

```
SendMessage(
  type: "message",
  recipient: "agent-1",
  summary: "Phase 2: Opening statement",
  content: """
PHASE 2 — OPENING STATEMENT

You are first. Pick the single best product from the verified list for your persona.

Verified products: <VERIFIED_PRODUCTS_LIST>

State:
1. Your pick (must be from verified list only)
2. Three strongest reasons for your pick
3. One honest weakness

Write to: debate-output/phase2/agent-1.md
Max 300 words.
"""
)
```

**Middle speakers (agent-2 through agent-N-1):**

```
SendMessage(
  type: "message",
  recipient: "agent-<N>",
  summary: "Phase 2: Opening statement",
  content: """
PHASE 2 — OPENING STATEMENT

Picks already taken: <PRIOR_PICKS>
You MUST pick a different product than those already claimed.

Verified products: <VERIFIED_PRODUCTS_LIST>
Your persona: <PERSONA_NAME> — <PERSONA_DESCRIPTION>

State:
1. Your pick (must be from verified list, must not duplicate prior picks)
2. Three strongest reasons
3. One honest weakness

Write to: debate-output/phase2/agent-<N>.md
Max 300 words.
"""
)
```

**Final speaker (Contrarian persona):**

```
SendMessage(
  type: "message",
  recipient: "agent-<N>",
  summary: "Phase 2: Opening statement — contrarian",
  content: """
PHASE 2 — OPENING STATEMENT (CONTRARIAN)

All prior picks: <PRIOR_PICKS>

Your role: Find the overlooked option. Pick the product that others have ignored but deserves serious consideration. It must be from the verified list and not already claimed.

State:
1. Your pick
2. Why it's underrated or overlooked
3. Three specific strengths others miss
4. One honest weakness

Write to: debate-output/phase2/agent-<N>.md
Max 300 words.
"""
)
```

After all opening statements, check for duplicates:

```bash
python3 scripts/debate_orchestrator.py check-duplicates
```

If duplicates found: re-send to the duplicate agent with forced disagreement prompt including all unique picks so far.

---

## Phase 3 — Debate Rounds

Run 2-3 rounds. Word limits decrease each round: 500 → 400 → 300.

**For each round R:**

**Step 1 — Build per-agent context:**

Read prior round files from `debate-output/phase2/` (round 1) or `debate-output/phase3/round-<R-1>/` (round 2+). For each agent, embed the raw text of all other agents' positions in the SendMessage content. Include the issue tracker contents if available.

Do NOT summarize — pass raw text through verbatim.

**Step 1.5 — Private deliberation (rounds 2+ only):**

Before the public debate round, pair agents for private critique exchanges. Use round-robin pairing (each agent paired with 1-2 others):

```
SendMessage(
  type: "message",
  recipient: "agent-<A>",
  summary: "Private critique of agent-<B>'s position",
  content: """
PRIVATE DELIBERATION — Round <R>

Read agent-<B>'s most recent position. Write a private critique (max 150 words) focusing on their single weakest argument. Be direct — this is private, not public.

Write to: /tmp/debate-session/phase3/round-<R>/private/agent-<A>-to-agent-<B>.md
"""
)
```

Wait for all private critiques. Include private notes in each agent's context for the public round.

**Step 2 — Send debate tasks (parallel):**

```
For each agent-N:
SendMessage(
  type: "message",
  recipient: "agent-<N>",
  summary: "Phase 3: Debate round <R>",
  content: """
PHASE 3 — DEBATE ROUND <R>

<RAW_TEXT_OF_ALL_OTHER_AGENTS_PRIOR_POSITIONS>

<ISSUE_TRACKER_CONTENTS_IF_AVAILABLE>

<PRIVATE_DELIBERATION_NOTES_IF_ANY>

Your task:
1. Defend your pick against specific criticisms raised
2. Challenge the strongest competing pick (name it, cite specifics)
3. Update your argument based on what you've learned

Word limit: <WORD_LIMIT>
Write to: debate-output/phase3/round-<R>/agent-<N>.md
"""
)
```

**Step 3 — Judge evaluates round + convergence assessment:**

After each debate round, send the judge all round output. The judge's evaluation MUST include a `Convergence Assessment` section with a `Recommendation:` line (`continue`, `converged`, or `stalled`).

Parse the judge's `Recommendation:` line from the SendMessage response:
- `converged` → skip remaining rounds, go to Phase 4
- `stalled` → skip remaining rounds, go to Phase 4
- `continue` → proceed to next round

Log:

```bash
echo "[$(date '+%H:%M:%S')] ROUND — Round <R> complete. Convergence: <RESULT>" >> debate-output/debate.log
```

---

## Phase 4 — Elimination

**Goal:** Vote down all but two finalists.

**Voting (parallel):**

```
For each agent-N:
SendMessage(
  type: "message",
  recipient: "agent-<N>",
  summary: "Phase 4: Elimination vote",
  content: """
PHASE 4 — ELIMINATION VOTE

Current products still in contention: <PRODUCTS_LIST>

Vote to eliminate ONE product. This should NOT be your own pick.

Provide:
1. Product to eliminate
2. Confidence level (1-10)
3. Specific reasoning (cite debate arguments)

Write to: /tmp/debate-session/phase4/vote-agent-<N>.md
"""
)
```

After all votes:

```bash
python3 scripts/vote_tallier.py /tmp/debate-session/phase4/
```

**Tiebreak sequence (follow strictly — do not override with manual judgment):**
1. Plurality (most votes to eliminate)
2. Highest confidence among tied products
3. Cumulative vote weight across prior rounds
4. Jury tiebreak (exit code 2 from vote_tallier)

**If jury tiebreak (exit code 2):** Read `elimination-results.json` to get the `tied_products` list. Then:

1. For each tied product, identify its champion agent
2. Send each champion a brief defense task (max 200 words)
3. Send the judge a tiebreak ruling task
4. Parse the judge's ruling and continue elimination.

Repeat elimination rounds until exactly 2 finalists remain.

**User gate:** Report finalists and eliminated products, ask to proceed to Phase 5.

---

## Phase 5 — Finals

**Head-to-head debate (parallel):**

Send each finalist champion a defense task (max 400 words). Then a forced revision where each champion reads the opponent's defense and writes a revised version (max 300 words).

**Two-step judge evaluation:**

Step 1 — Strip to facts:
```
SendMessage(
  type: "message",
  recipient: "judge",
  summary: "Phase 5: Strip arguments to facts",
  content: """
Read both defenses and revisions. Extract only verifiable factual claims. Strip advocacy language.
Write fact sheet to: /tmp/debate-session/phase5/facts.md
"""
)
```

Step 2 — Fresh evaluation using ONLY the fact sheet and opening statements from Phase 2. Issue judgment with winner, three decisive factors, and runner-up strengths.

**Forced revision of judgment:** Generate 2-3 devil's advocate concerns, revise if compelling.

**Jury validation:** Eliminated agents serve as jurors. VALIDATED/CHALLENGED verdict. Majority rules.

---

## Phase 6 — Synthesis

**Step 1 — Compile evidence:**

```bash
python3 scripts/debate_orchestrator.py compile-synthesis
```

Read `evidence.json` to get all debate data.

**Step 2 — Build structured synthesis prompt:**

Send to synthesizer agent with full evidence. Required output:
1. Recommendation with buy link (verified via WebFetch)
2. Comparison table — ALL products from Phase 1
3. Why [Winner] wins — reference debate evidence only
4. The Case for [Runner-up] — specific scenarios with buy link
5. What the Debate Missed — evidence gaps, market factors, biases
6. Sources — deduplicated URLs by product

**Step 3 — Spawn synthesizer (if not already a team member).**

**3-level fallback:**
1. Primary: synthesizer completes with all sections
2. Backup: simplified prompt
3. Last resort: concatenate raw phase outputs

**Validate buy links:** WebFetch each link. Replace broken links with search URLs.

Present `debate-output/final-report.md` to the user.
