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
| judge | Assesses complexity, evaluates arguments, fact-checks, issues rulings |
| debater (×2-5) | Domain-specific debaters with tailored personas |

## Output

- `debate-output/` — round files, issue tracker, debate log
- `/tmp/debate-session/` — session state, phase files
- Final output: synthesis.md (product) or Judge's Ruling (topic)

## Configuration

Override models in your project's `.claude/settings.json`:
```json
{
  "agent": {
    "debate-lead": { "model": "opus" },
    "judge": { "model": "opus" },
    "debater": { "model": "sonnet" }
  }
}
```

## Prerequisites

- Python 3.10+
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (set in plugin settings.json)
- Optional MCP servers: scrapling-fetch, perplexity-mcp
