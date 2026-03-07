# Task Description Templates

Reference templates for the debate lead to use when building SendMessage content. Populate placeholders with real data from state and prior round files.

---

## Context Threading

Passing context cleanly between agents is critical. Follow this discipline:

- **Issue tracker:** Always read the latest `debate-output/issue-tracker.md` and include the full contents in every round task (topic mode)
- **Prior positions:** Read all files from the previous round's output directory; include the full text in task content
- **Raw embedding:** Always embed the full raw text of prior round outputs in task descriptions — never summarize them yourself. Summarization introduces bias.
- **Private deliberation notes:** If judge writes private notes, include them in the judge's next task description (not shared with debaters)
- **Source material paths:** Always include explicit file paths in every task description so agents can read them directly

Never summarize prior positions yourself. Pass the raw text. Summarization introduces bias.

---

## Research Sprint (Product Mode)

```
PHASE 1 — RESEARCH SPRINT

Topic: <TOPIC>
Your persona: <PERSONA_NAME> — <PERSONA_DESCRIPTION>

Research products that address this topic. For each candidate document:
- Product name and public URL
- Core differentiator in one sentence
- Price range or pricing model
- Best suited for which user type or use case
- Your persona's one-line verdict

Output file: /tmp/debate-session/phase1/agent-<N>.md

Aim for 5-8 products. Only include products with real, verifiable public URLs.
```

---

## Opening Statement (Product Mode — Position Aware)

```
PHASE 2 — OPENING STATEMENT

Topic: <TOPIC>
Verified products: <VERIFIED_PRODUCTS_LIST>
Your persona: <PERSONA_NAME> — <PERSONA_DESCRIPTION>

[If middle speaker]:
Picks already claimed: <PRIOR_PICKS>
You MUST choose a product not already claimed.

[If contrarian speaker]:
All claimed picks: <PRIOR_PICKS>
You MUST find the overlooked option — a product from the verified list that no one else has claimed.

Declare your single top pick. Include:
1. Your pick (from verified list only)
2. Three strongest reasons
3. One honest weakness

Output file: debate-output/phase2/agent-<N>.md
Max 300 words.
```

---

## Debate Round (Product Mode)

```
PHASE 3 — DEBATE ROUND <R>

Topic: <TOPIC>
Your persona: <PERSONA_NAME> — <PERSONA_DESCRIPTION>

<RAW_TEXT_OF_ALL_OTHER_AGENTS_PRIOR_POSITIONS>

Your task:
1. Defend your pick against specific criticisms raised in prior rounds
2. Directly challenge the strongest competing pick (name it, cite specific weaknesses)
3. Update your argument based on what the debate has revealed

Output file: debate-output/phase3/round-<R>/agent-<N>.md
Word limit: <WORD_LIMIT>
```

---

## Debate Round (Topic Mode)

```
ROUND <R>

Topic: <TOPIC>
Your persona: <PERSONA_NAME> — <PERSONA_DESCRIPTION>

Issue tracker (current):
---
<ISSUE_TRACKER_CONTENTS>
---

Prior round positions:
---
<PRIOR_ROUND_POSITIONS>
---

Your task:
1. Respond to the strongest argument made against your position
2. Advance your thesis with new reasoning or evidence
3. Address at least one open issue from the tracker directly
4. Concede ground where warranted — intellectual honesty is scored

Output file: debate-output/round-<R>/agent-<N>.md
Max 400 words.
```

---

## Judge Assessment (Standard)

```
Assess this query and return ONLY a raw JSON object (no markdown fences, no explanation):

Query: <TOPIC>

{
  "mode": "product" or "topic",
  "agent_count": <integer 2-5>,
  "personas": [
    {"name": "<name>", "description": "<role description>", "stance": "<initial stance or lens>", "role": "challenger|defender|balanced"}
  ],
  "round_count": <integer 2-5>,
  "rationale": "<why this configuration>"
}

At least one persona must have role "challenger" and at least one "defender".
```

---

## Judge Assessment (Final Round — Topic Mode)

```
This is the FINAL round of the debate.

Read all debate output: debate-output/
Read the complete issue tracker: debate-output/issue-tracker.md

Issue your binding JUDGE'S RULING. You MUST include all three sections:

1. Per-issue verdicts
   For each issue in the tracker: which position prevailed and the decisive reasoning.

2. Quality metrics
   Rate each debater: evidence quality (1-10), logical consistency (1-10), responsiveness to opponents (1-10).

3. Overall verdict
   Which position or synthesis is most defensible. Why.

Output: debate-output/final-ruling.md
This ruling is binding and final.
```

---

## Elimination Vote (Product Mode)

```
PHASE 4 — ELIMINATION VOTE

Products still in contention: <PRODUCTS_LIST>

Vote to eliminate ONE product. Do not vote against your own pick.

Provide:
1. Product to eliminate (name exactly as listed)
2. Confidence level (1-10)
3. Specific reasoning citing arguments from the debate

Output file: /tmp/debate-session/phase4/vote-agent-<N>.md
```

---

## Finals Defense (Product Mode)

```
PHASE 5 — FINALS

You are defending: <PRODUCT_A>
Your opponent is defending: <PRODUCT_B>

Write your strongest defense. Focus on:
1. Concrete use-case wins for your product
2. Specific weaknesses of the competing product with evidence
3. Evidence drawn from the full debate

Max 400 words.
Output: debate-output/phase5/defense-<PRODUCT_A>.md

After writing, read your opponent's defense at debate-output/phase5/defense-<PRODUCT_B>.md and write a revised defense that directly addresses their strongest points.
Revised output: debate-output/phase5/revised-<PRODUCT_A>.md
Max 300 words.
```

---

## Synthesis (Product Mode)

```
SYNTHESIS — Final Report

Read all debate output from: debate-output/
Final judgment: debate-output/phase5/final-judgment.md
Phase 2 opening statements: debate-output/phase2/

Write the final synthesis report to: debate-output/final-report.md

Structure:
1. Executive summary (winner and decisive factors)
2. Full comparison table (all finalists, key dimensions)
3. Runner-up analysis (strengths worth considering)
4. Who should choose what (user type segmentation)
5. Buy links for all products

Do not inject new opinions. Synthesize what the debate produced.
```
