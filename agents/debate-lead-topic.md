# Topic Mode Execution

Topic mode is round-based with an issue tracker maintained by the judge.

---

## Setup

Judge recommends round count and personas. Lead spawns N agents as described in Setup Phase. Store `TOTAL_ROUNDS` privately — **never share this with debaters**.

---

## Resume Detection

Before starting rounds, check for existing output from a prior interrupted run:

1. Glob for `debate-output/round-*/agent-*.md`
2. If files exist, determine the last complete round (a round is complete when all agents have written their file)
3. Check if `debate-output/issue-tracker.md` exists (confirms judge evaluated that round)
4. If a complete round is found:
   - Log: `"[HH:MM:SS] RESUME — Found existing rounds 1-N. Resuming from round N+1."`
   - Set the starting round to N+1 and skip to "Rounds 2 through N" section
5. If no files exist or the only round is incomplete, start fresh from Round 1

---

## Round 1 — Opening Positions

Round 1 runs **sequentially** with defenders first, then balanced, then challengers last. This ensures challengers can directly attack existing positions rather than arguing in a vacuum.

**Ordering:** Defenders first → Balanced second → Challengers last. Within each group, order by agent number.

Determine the ordering from the judge's persona list:
1. Collect all agents with role `defender` → sorted by agent number
2. Collect all agents with role `balanced` → sorted by agent number
3. Collect all agents with role `challenger` → sorted by agent number
4. Final order = defenders + balanced + challengers

**For each agent in the sequential order:**

If this is the first agent, they build their position from scratch:

```
SendMessage(
  type: "message",
  recipient: "agent-<N>",
  summary: "Round 1: Opening position",
  content: """
ROUND 1 — OPENING POSITION

Topic: <TOPIC>
You are in round 1 of the debate. This is the opening round.
Your persona: <PERSONA_NAME> — <PERSONA_DESCRIPTION>

Present your opening position:
1. Core thesis (1-2 sentences)
2. Three supporting arguments with evidence or reasoning
3. One preemptive rebuttal of the most obvious counterargument

Write to: debate-output/round-1/agent-<N>.md
Max 400 words.
"""
)
```

For subsequent agents, include the raw text of all prior submissions from this round:

```
SendMessage(
  type: "message",
  recipient: "agent-<N>",
  summary: "Round 1: Opening position",
  content: """
ROUND 1 — OPENING POSITION

Topic: <TOPIC>
You are in round 1 of the debate. This is the opening round.
Your persona: <PERSONA_NAME> — <PERSONA_DESCRIPTION>

Positions already submitted this round:
---
<RAW_TEXT_OF_ALL_PRIOR_AGENT_SUBMISSIONS>
---

Present your opening position:
1. Core thesis (1-2 sentences)
2. Three supporting arguments with evidence or reasoning
3. One preemptive rebuttal of the most obvious counterargument
4. Direct response to at least one prior position (if any exist)

Write to: debate-output/round-1/agent-<N>.md
Max 400 words.
"""
)
```

Wait for each agent to respond before sending to the next agent.

After all agents respond, send to judge:

```
SendMessage(
  type: "message",
  recipient: "judge",
  summary: "Round 1: Evaluate and create issue tracker",
  content: """
Round 1 positions are complete.

Opening statements:
---
<READ_AND_EMBED_ALL_ROUND_1_AGENT_FILES>
---

(Files also available at: debate-output/round-1/)

Evaluate each position and create the issue tracker. The issue tracker should list:
- Key contested claims
- Points of agreement (if any)
- Logical gaps or unsupported assertions
- Questions that remain unresolved

Write issue tracker to: debate-output/issue-tracker.md
Write your round evaluation to: debate-output/evaluations/round-1.md
"""
)
```

After each agent writes their file, log immediately:

```bash
WC=$(wc -w < debate-output/round-1/agent-<N>.md)
echo "[$(date '+%H:%M:%S')] WRITTEN — debate-output/round-1/agent-<N>.md submitted ($WC words, limit: 400)" >> debate-output/debate.log
```

After judge creates the tracker:

```bash
echo "[$(date '+%H:%M:%S')] TRACKER — Round 1 created. Resolved: 0, Open: N, Stalled: 0" >> debate-output/debate.log
echo "[$(date '+%H:%M:%S')] ROUND — Round 1 complete. Issue tracker created." >> debate-output/debate.log
```

---

## Rounds 2 through N

For each subsequent round R, agents go **sequentially** (not parallel). This creates real adversarial clash — each agent responds to the latest output, not just the previous round.

**Ordering:** Challengers first → Defenders second → Balanced last. Within each group, order by agent number.

Determine the ordering from the judge's persona list:
1. Collect all agents with role `challenger` → sorted by agent number
2. Collect all agents with role `defender` → sorted by agent number
3. Collect all agents with role `balanced` → sorted by agent number
4. Final order = challengers + defenders + balanced

**For each agent in the sequential order:**

**Step 1 — Build this agent's context (hybrid approach):**

Read prior round files and any already-submitted files from this round. Use hybrid context threading:
- **Round 2:** Inline round 1 outputs (only one prior round — small enough to embed)
- **Round 3+:** Reference rounds 1 through R-2 by file path only; inline only round R-1 outputs
- **Always inline:** Current round's already-submitted outputs, issue tracker contents, their own prior position
- **Never summarize** — either embed raw text or provide file paths

Do NOT summarize — pass raw text through verbatim.

**Step 2 — Send debate task to this agent (wait for response before next):**

```
SendMessage(
  type: "message",
  recipient: "agent-<N>",
  summary: "Round <R>: Respond and advance",
  content: """
ROUND <R>

Topic: <TOPIC>
You are in round <R> of the debate.
Your persona: <PERSONA_NAME> — <PERSONA_DESCRIPTION>

Issue tracker (current):
---
<READ_AND_EMBED_ISSUE_TRACKER_CONTENTS>
---

[IF R == 2: inline round 1 outputs]
Prior round positions:
---
<READ_AND_EMBED_ROUND_1_FILES>
---

[IF R >= 3: reference earlier rounds by path, inline only round R-1]
Prior rounds (read these files for full context):
- debate-output/round-1/agent-1.md
- debate-output/round-1/agent-2.md
- ... (list all prior round files through round R-2)

Most recent round positions (round <R-1>):
---
<READ_AND_EMBED_ROUND_R-1_FILES>
---

Already submitted this round:
---
<READ_AND_EMBED_ANY_CURRENT_ROUND_FILES>
---

Your task:
1. Respond to the strongest argument made against your position
2. Advance your thesis with new reasoning or evidence
3. Address at least one open issue from the tracker
4. Identify one point where you concede ground (if warranted)

Write to: debate-output/round-<R>/agent-<N>.md
Max 400 words.
"""
)
```

Wait for this agent to respond and write their file before proceeding to the next agent in the sequence.

After each agent writes, log:

```bash
WC=$(wc -w < debate-output/round-<R>/agent-<N>.md)
echo "[$(date '+%H:%M:%S')] WRITTEN — debate-output/round-<R>/agent-<N>.md submitted ($WC words, limit: 400)" >> debate-output/debate.log
```

**Step 3 — Judge evaluates and updates tracker:**

```
SendMessage(
  type: "message",
  recipient: "judge",
  summary: "Round <R>: Evaluate and update tracker",
  content: """
Round <R> is complete.

Round <R> responses:
---
<READ_AND_EMBED_ALL_ROUND_R_AGENT_FILES>
---

(Files also available at: debate-output/round-<R>/)

Update the issue tracker based on what was argued this round:
- Mark resolved issues as resolved (with verdict)
- Add newly surfaced issues
- Note shifts in debater positions

Write updated tracker to: debate-output/issue-tracker.md
Write evaluation to: debate-output/evaluations/round-<R>.md

If you believe the debate has reached sufficient resolution before the final round, include "terminate": true in your response JSON.
"""
)
```

**Step 4 — Check for early termination:**

After judge updates the tracker, log:

```bash
echo "[$(date '+%H:%M:%S')] TRACKER — Round <R> updated. Resolved: N, Open: N, Stalled: N" >> debate-output/debate.log
```

Parse judge's response. Check **both** termination signals:
1. `"terminate": true` in the judge's JSON response
2. The text `JUDGE'S RULING` appears anywhere in the judge's response

If either signal is present, stop rounds and proceed to Final Round immediately.

Log each round:

```bash
echo "[$(date '+%H:%M:%S')] ROUND — Round <R>/<TOTAL> complete. Terminate: <YES/NO>" >> debate-output/debate.log
```

If early termination:

```bash
echo "[$(date '+%H:%M:%S')] ROUND — Early termination triggered by judge at round <R>" >> debate-output/debate.log
```

---

## Final Round

Tell the judge this is the final round. This is mandatory.

```
SendMessage(
  type: "message",
  recipient: "judge",
  summary: "Final round: Issue binding ruling",
  content: """
This is the FINAL round of the debate.

Read all debate output: debate-output/
Read the complete issue tracker: debate-output/issue-tracker.md

You MUST issue a binding JUDGE'S RULING. This ruling must include:
1. Per-issue verdicts — for each tracked issue, state which position prevailed and why
2. Quality metrics — rate each debater's argumentation (evidence quality, logical consistency, responsiveness)
3. Overall verdict — which position (or synthesis) is most defensible, and why

This ruling is final. Write it to: debate-output/final-ruling.md
"""
)
```

If judge fails to issue a ruling: retry the SendMessage. The ruling is mandatory — do not proceed without it.

Log:

```bash
echo "[$(date '+%H:%M:%S')] RULING — Final ruling received. Writing complete." >> debate-output/debate.log
```

---

## Optional: Post-Ruling Synthesis

Check whether the original spawn included a `<synthesize>true</synthesize>` tag. If so, spawn a synthesizer to produce a final synthesis document.

**Step 1 — Spawn synthesizer as a team member:**

```
Task(
  subagent_type: "claude-debate:synthesizer",
  name: "synthesizer",
  team_name: "debate",
  prompt: "You are the synthesizer. Follow your agent instructions exactly. Wait for assignments."
)
```

**Step 2 — Send synthesis task:**

```
SendMessage(
  type: "message",
  recipient: "synthesizer",
  summary: "Synthesize topic debate",
  content: """
TOPIC MODE SYNTHESIS

Read all debate output from: debate-output/
Read the final ruling: debate-output/final-ruling.md
Read the issue tracker: debate-output/issue-tracker.md

Write a synthesis report to: debate-output/synthesis.md

Follow your Topic Mode Synthesis instructions. Synthesize only what the debate and judge produced — no new analysis.
"""
)
```

Log:

```bash
echo "[$(date '+%H:%M:%S')] HANDOVER — Synthesis spawned for topic mode" >> debate-output/debate.log
```

If synthesis was not requested (no `<synthesize>` tag or `<synthesize>false</synthesize>`), skip this section entirely.
