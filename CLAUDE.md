# claude-debate

Multi-agent adversarial debate plugin using Team agents.

## Usage

```
/claude-debate:start "best ergonomic keyboard under $200"
/claude-debate:start "Should companies mandate return to office?"
/claude-debate:start --rounds 3 "Is nuclear energy the best path to decarbonization?"
/claude-debate:cleanup
```

## How It Works

1. Judge assesses the query → recommends mode, agent count (2-5), personas, rounds
2. Lead spawns N debater Team agents with judge-recommended personas
3. Debate runs (product mode: 6-phase tournament, topic mode: round-based with issue tracking)
4. Output written to `debate-output/` and `/tmp/debate-session/`

## Modes

**Product mode** (buying/comparing): Research → Opening Statements → Debate Rounds → Elimination → Finals → Synthesis
**Topic mode** (questions/debates): Opening Positions → Debate Rounds with Issue Tracker → Judge's Ruling

## Agents

| Agent | Role |
|-------|------|
| debate-lead | Orchestrator — manages lifecycle, rounds, output |
| judge | Assesses complexity, evaluates arguments, fact-checks with WebSearch/WebFetch, issues rulings |
| challenger | Adversarial critic — 6-dimension critique framework, attacks positions, fact-checks opponents |
| defender | Rigorous advocate — structured defense labeling (DEFENDED/NEEDS TIGHTENING/VULNERABLE) |
| debater | Balanced role — equal critique and defense (used for balanced personas) |
| synthesizer | Final report writer — product mode only, synthesizes debate evidence into recommendation |

## Configuration

Override models in your project's `.claude/settings.json`:
```json
{
  "agent": {
    "debate-lead": { "model": "opus" },
    "judge": { "model": "opus" },
    "challenger": { "model": "sonnet" },
    "defender": { "model": "sonnet" },
    "debater": { "model": "sonnet" },
    "synthesizer": { "model": "sonnet" }
  }
}
```

## Debate Flow

**Product mode (6 phases):** Research → Opening Statements → Debate Rounds → Elimination → Finals → Synthesis

**Topic mode:**
- Round 1: Agents present opening positions **sequentially** (defenders → balanced → challengers) so challengers can attack existing positions → Judge evaluates, creates issue tracker
- Round 2+: Agents go **sequentially** (challengers → defenders → balanced) so each responds to latest output → Judge updates tracker, can terminate early
- Final: Judge issues binding JUDGE'S RULING with per-issue verdicts, points of agreement, concessions, dismissed arguments, unresolved disagreements, and quality metrics

## Context Threading

The debate-lead threads context between rounds via:
- **Issue tracker**: A running file (`issue-tracker.md`) in the output directory, updated after each round based on the judge's assessment. Tracks resolved, open, and stalled issues.
- **Task descriptions**: Each round's task descriptions include the issue tracker contents and raw text of prior round outputs, so agents have full context without summarization bias.

## Output

Results are written to the output directory:

```
debate-output/
  round-1/
    agent-1.md
    agent-2.md
    ...
  round-2/
    ...
  evaluations/
    round-1.md
    round-2.md
  issue-tracker.md
  final-ruling.md (topic) or final-report.md (product)
  debate.log
```

## Agent Files

Agent instructions live in `agents/`:
- `debate-lead.md` — orchestrator: setup, error recovery, logging, cleanup, execution rules
- `debate-lead-product.md` — product mode phases (research → opening → debate → elimination → finals → synthesis)
- `debate-lead-topic.md` — topic mode execution (sequential rounds, issue tracking, final ruling)
- `debate-lead-templates.md` — task description templates and context threading rules
- `judge.md` — impartial arbiter, assessor, fact-checker with verification protocol, convergence assessment, ruling authority
- `challenger.md` — adversarial critic with 6-dimension critique framework (agreement intensity: 5)
- `defender.md` — rigorous advocate with 5-dimension defense framework (agreement intensity: 8)
- `debater.md` — balanced debater with equal critique/defense weight (agreement intensity: 7)
- `synthesizer.md` — final report writer (product mode only)

## Prerequisites

- Python 3.10+
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (set in plugin settings.json)
- Optional MCP servers: scrapling-fetch, perplexity-mcp
