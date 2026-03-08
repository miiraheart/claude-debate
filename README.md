# claude-debate

Multi-agent adversarial debate plugin for Claude Code. A dynamic team of 2-5 agents argues any topic or researches any product through structured rounds with fact-checking, elimination, and binding rulings.

## Features

- Dynamic agent scaling (2-5 debaters, judge decides)
- Dual mode: product research (6-phase tournament) and topic debate (issue tracking + verdicts)
- Fact-checking with CONFIRMED/DISPUTED/FABRICATED labels
- Citation accountability ([Unsourced] marking)
- Convergence detection (keyword agreement + Jaccard stability)
- 4-step vote tiebreak chain
- 2-step judge evaluation (strip to facts → fresh evaluation)
- Forced revision (devil's advocate challenges)
- Jury validation by eliminated agents
- Error recovery (agent failure handling)
- Issue tracker across rounds
- Hidden round count (prevents convergence pressure)
- Domain-aware persona selection

## Quick Start

```bash
# Install
git clone https://github.com/miiraheart/claude-debate.git ~/.claude/plugins/claude-debate
# Or via marketplace (when available):
# claude plugin add miiraheart/claude-debate

# Run
/claude-debate:start "best noise-cancelling headphones under $300"
/claude-debate:start "Should we adopt microservices or keep our monolith?"
/claude-debate:start --rounds 4 "Is UBI economically feasible?"

# Cleanup
/claude-debate:cleanup
/claude-debate:cleanup all  # also removes session files
```

## Prerequisites

- Claude Code CLI
- Python 3.10+
- Team agents enabled automatically via plugin settings

### Optional MCP Servers

**scrapling-fetch** (bot-protected pages):
```bash
uv tool install scrapling-fetch-mcp
```
Add to `~/.claude.json`:
```json
{
  "mcpServers": {
    "scrapling-fetch": {
      "command": "scrapling-fetch-mcp",
      "args": []
    }
  }
}
```

**perplexity-mcp** (enhanced search):
Install via [Smithery](https://smithery.ai/server/@nicholasharbin/perplexity-search-mcp) or manually:
```json
{
  "mcpServers": {
    "perplexity-mcp": {
      "command": "npx",
      "args": ["-y", "perplexity-search-mcp"],
      "env": {
        "PERPLEXITY_API_KEY": "your-api-key"
      }
    }
  }
}
```

## How It Works

```
User: /claude-debate:start "query"
  │
  ├── Judge assesses query → { mode, agents: 2-5, personas, rounds }
  │
  ├── Product Mode                    ├── Topic Mode
  │   Phase 1: Research Sprint        │   Round 1: Opening Positions
  │   Phase 2: Opening Statements     │   Round 2+: Debate + Issue Tracker
  │   Phase 3: Debate Rounds          │   Final: Judge's Ruling
  │   Phase 4: Elimination            │
  │   Phase 5: Finals + Jury          │
  │   Phase 6: Synthesis              │
```

## Configuration

Default: Opus for lead+judge, Sonnet for debaters+synthesizer. Override in `.claude/settings.json`:
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

## Project Structure

```
claude-debate/
├── .claude-plugin/plugin.json
├── agents/
│   ├── debate-lead.md        # Orchestrator — manages lifecycle, rounds, output
│   ├── judge.md              # Impartial arbiter, fact-checker, ruling authority
│   ├── challenger.md         # Adversarial critic — 6-dimension critique framework
│   ├── defender.md           # Rigorous advocate — structured defense labeling
│   ├── debater.md            # Balanced role — equal critique and defense
│   └── synthesizer.md        # Final report writer (product mode only)
├── skills/
│   ├── start/SKILL.md
│   └── cleanup/SKILL.md
├── scripts/
│   ├── debate_orchestrator.py
│   ├── convergence_detector.py
│   └── vote_tallier.py
├── style-guides/claude-debate.md
├── prompts/
│   ├── personas.md
│   └── synthesizer.md
├── settings.json
├── CLAUDE.md
└── README.md
```

## Research Foundations

| Technique | Source |
|-----------|--------|
| Multi-Agent Debate (MAD) | Du et al. 2023, Tsinghua |
| Agreement intensity | DebateLLM, google_ma_debate.yaml |
| Convergence detection | Judge inline assessment |
| Elimination voting | elimination_game |
| 2-step judge | MAD interactive.py |
| Forced revision | agent-for-debate |
| Jury validation | elimination_game finals |
| Domain personas | DyLAN (debate-or-vote) |
| Dense topology | debate-or-vote |
| Issue tracking | agent-debate |

## License

MIT
