# Claude Debate Output Style

## Citation Format

All agent outputs must use inline citations. Every major claim requires a citation — either a verified source or an explicit unsourced marker.

### Sourced Claims

```
The recidivism rate was 43% [Source: "Title of Paper", Author, Year](https://example.com/paper)
```

### Unsourced Claims

```
This suggests a broader trend [Unsourced -- analytical reasoning, not empirically verified]
```

### Standard Links

```
See [Stanford Law Review analysis](https://example.com/article) for details
```

### Fact-Check Results (Judge Only)

```markdown
## Fact-Check Report

### Verified Claims
- Claim by Agent: CONFIRMED -- [Source corroborates](URL)

### Disputed Claims
- Claim by Agent: DISPUTED -- Source says X, not Y

### Fabricated Citations
- Agent cited "Non-Existent Paper" -- this source does not appear to exist
```

---

## Output Structure — Topic Mode

Each round gets its own folder with independent files per agent:

```
debate-output/
  round-1/
    agent-1.md
    agent-2.md
    ...
    judge.md
  round-2/
    ...
  issue-tracker.md
  debate.log
```

### Agent Files

Each agent file follows this structure:

```markdown
# Round N — [Persona Name]

[Structured argument or critique with severity ratings and citations]
```

### `judge.md`

```markdown
# Round N — Judge

[Impartial evaluation of all sides, including fact-check report]
```

---

## Output Structure — Product Mode

```
/tmp/debate-session/                    (intermediate session data)
  phase1/agent-{N}.md                   (research sprint)
  phase4/vote-agent-{N}.md              (elimination votes)
  phase5/facts.md                       (stripped facts)
  state.json

debate-output/                          (primary output)
  phase2/agent-{N}.md                   (opening statements)
  phase3/round-{R}/agent-{N}.md         (debate rounds)
  phase5/defense-*.md, revised-*.md     (finals)
  phase5/judgment.md, final-judgment.md (judge verdicts)
  final-report.md                       (synthesis — final output)
  debate.log
```

---

## Final Synthesis Structure — Product Mode

```markdown
### Recommendation
**[Winner]** — [one-sentence verdict]
**Buy here**: [direct product link]

### Comparison Table
| | Winner | Runner-up | Eliminated 1 | ... |
|---|---|---|---|---|
| Price | | | | |
| [Key Spec] | | | | |
| Best for | | | | |
| Worst for | | | | |
| Verdict | WINNER | Runner-up | Eliminated | |

### Why [Winner] Wins
[2-3 paragraphs with evidence references]

### The Case for [Runner-up]
**Buy here**: [direct product link]
[Scenarios where runner-up is better]

### What the Debate Missed
[Evidence gaps, market factors, biases]

### Sources
[Deduplicated URLs by product]
```

---

## JUDGE'S RULING Structure — Topic Mode

```markdown
## JUDGE'S RULING

### Per-Issue Verdicts
[For each open issue:]
- **[Issue]**: ACCEPTED / REJECTED / REVISION REQUIRED
  - Reasoning: [why]
  - Evidence quality: [assessment of sources cited by all sides]

### Points of Agreement
[Issues where sides converged during the debate]

### Concessions
[What each side conceded during the debate and why]

### Dismissed Arguments
[Arguments the judge found unpersuasive from any side, with reasoning]

### Unresolved Disagreements
[Issues that remained genuinely contested through the end]

### Quality Metrics
- **Citations verified**: N confirmed, N disputed, N fabricated
- **Issues resolved**: N of M total
- **Issues stalled**: N (argued 2+ rounds without progress)
- **Argument evolution**: [Did arguments meaningfully develop across rounds, or mostly repeat?]

### Overall Verdict
[Judge's final assessment of the position as a whole]
```

---

## Formatting Guidelines

- Clear markdown headers for structure
- Quote specific arguments when referencing them
- Bullet points for lists of issues or arguments
- Severity ratings where applicable: **Critical** / **Major** / **Minor**
- Precise, analytical language — no rhetorical flourishes in summaries
- Every major claim must have an inline citation — unsourced claims must be explicitly marked
- Markdown tables for counterargument assessments and product comparisons
