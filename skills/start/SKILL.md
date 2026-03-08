---
name: start
description: Launch a multi-agent adversarial debate with a dynamic team of 2-5 agents on any topic or product query
---

You are launching the **claude-debate** plugin — a multi-agent adversarial debate system.

The user's raw input is: `$ARGUMENTS`

## Argument Parsing

1. **Check for `--rounds N` flag**: Scan `$ARGUMENTS` for `--rounds <value>`. If found, extract `<value>` as the candidate round count and remove the flag from the arguments.
2. **Check for `--synthesize` flag**: Scan `$ARGUMENTS` for `--synthesize`. If found, set `SYNTHESIZE` to `true` and remove the flag. Otherwise set `SYNTHESIZE` to `false`.
3. **If no `--rounds` flag**: Set `ROUNDS` to `auto`. The remaining text after removing all flags is the `TOPIC`.
4. **If `TOPIC` is empty or whitespace-only** after parsing: Ask the user "What topic would you like to debate?" and wait for their response before proceeding.

### Input Validation

After parsing, validate **before** spawning the debate-lead:

- **`--rounds` value must be a positive integer**: If the value after `--rounds` is not a number (e.g. `--rounds abc`), is zero, negative, or a decimal, tell the user: "Invalid --rounds value '...'. Please provide a positive integer (e.g. --rounds 3)." and stop.
- **`--rounds` must be between 1 and 10**: If the number is outside this range, tell the user: "Rounds must be between 1 and 10. Got: N." and stop.
- **`TOPIC` must not be empty**: If no topic remains after extracting the flag, ask the user "What topic would you like to debate?" and wait.

Only proceed to spawn the debate-lead once both `ROUNDS` (a valid integer or `auto`) and `TOPIC` (non-empty string) are confirmed.

### Examples

- `--rounds 2 "Is water wet?"` → ROUNDS=2, SYNTHESIZE=false, TOPIC=`Is water wet?`
- `"Is water wet?" --rounds 4` → ROUNDS=4, SYNTHESIZE=false, TOPIC=`Is water wet?`
- `"Should AI have rights?"` → ROUNDS=auto, SYNTHESIZE=false, TOPIC=`Should AI have rights?`
- `--synthesize "Is nuclear energy viable?"` → ROUNDS=auto, SYNTHESIZE=true, TOPIC=`Is nuclear energy viable?`
- `--rounds 3 --synthesize "topic"` → ROUNDS=3, SYNTHESIZE=true, TOPIC=`topic`
- `--rounds abc "topic"` → error: invalid rounds value
- `--rounds 0 "topic"` → error: rounds must be between 1 and 10
- `--rounds 3` → ask for topic (empty after flag removal)

## Your job

Delegate entirely to the `debate-lead` agent by spawning it with the Task tool:

```
Task(
  subagent_type: "claude-debate:debate-lead",
  name: "debate-lead",
  prompt: "You are the debate lead. Launch and orchestrate a full adversarial debate. Follow your agent instructions in agents/debate-lead.md exactly.

<topic>TOPIC</topic>
<rounds>ROUNDS</rounds>
<synthesize>SYNTHESIZE</synthesize>",
  mode: "bypassPermissions"
)
```

Replace `TOPIC` with the parsed topic, `ROUNDS` with the parsed round count (a number or `auto`), and `SYNTHESIZE` with `true` or `false`.

The debate-lead agent handles everything: team creation, round orchestration, output writing, and cleanup.

Wait for the debate-lead to finish, then report the results to the user. Point them to the `debate-output/` directory for the full transcripts.
