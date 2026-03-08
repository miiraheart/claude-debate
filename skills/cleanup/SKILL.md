---
name: cleanup
description: Stop all debate agents, delete stale teams and tasks, clean up session files
---

You are running the **claude-debate cleanup** skill — it tears down any running or stale debate infrastructure.

## Steps

Perform all of the following:

### 1. Delete stale tasks

Call `TaskList` to get all tasks. For every task that exists, call `TaskUpdate` with `status: "deleted"` to remove it.

If there are no tasks, skip this step.

### 2. Clean up debate teams

Look for team config files. The Teams feature may store configs in different locations depending on the environment:
```bash
ls ~/.claude/teams/*/config.json 2>/dev/null || echo "No teams directory found"
```

If the directory does not exist, skip this step — there are no teams to clean up.

For each team whose description contains "debate" (case-insensitive):
1. Read the config to check for active members (judge + up to 5 debaters: agent-1, agent-2, etc.)
2. Send a `shutdown_request` to any active teammates
3. Remove the team directory and its matching task directory (if they exist):
   ```bash
   [ -d ~/.claude/teams/<team-name> ] && mv ~/.claude/teams/<team-name> /tmp/debate-cleanup-$(date +%s)/
   [ -d ~/.claude/tasks/<team-name> ] && mv ~/.claude/tasks/<team-name> /tmp/debate-cleanup-$(date +%s)/
   ```

**Do NOT delete teams that are not debate-related** (e.g., skip teams for other projects).

### 3. Clean up session files (only if requested)

If `$ARGUMENTS` contains "all" or "full", also remove debate session data:
```bash
rm -rf /tmp/debate-sessions/ /tmp/debate-session
rm -rf debate-output/
```

Otherwise, leave session data intact so the user can still review results.

### 4. Report

Tell the user what was cleaned up:
- How many tasks were deleted
- Which teams were removed
- Whether session data was cleared
