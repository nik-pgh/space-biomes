# Contributing to Space Biomes

This guide covers the workflow for both human contributors and autonomous coding agents.

## Prerequisites

- Node.js 18+, Python 3.9+, Yarn
- Git LFS installed (`git lfs install`)
- Bazel (for voxeloo C++ work only)
- See the [local setup guide](https://ill-inc.github.io/biomes-game/docs/basics/running-locally) for full environment setup

## Workflow overview

```
Issue → Branch → Implement → Validate → Commit → PR → Review → Merge
```

## 1. Issue intake

- Check [GitHub Issues](https://github.com/nik-pgh/space-biomes/issues) for assigned or relevant work
- Understand the issue scope before starting — read linked issues, related code, and any discussion
- If an issue is vague, ask for clarification before writing code
- Convert the issue into a concrete task: what files to change, what behavior to add/fix, how to validate

### Issue labels

| Label          | Meaning                                |
| -------------- | -------------------------------------- |
| `bug`          | Something is broken                    |
| `enhancement`  | New feature or improvement             |
| `docs`         | Documentation-only change              |
| `agent-safe`   | Pre-approved for autonomous agent work |
| `needs-review` | Requires human review before merge     |

## 2. Branching

Always work in a feature branch or git worktree. Never commit directly to `main`.

### Branch naming

```
<author>/<short-description>
```

- Use your name or `agent` as the author prefix
- Keep descriptions short and hyphenated
- Reference issue numbers when relevant

Examples:

```
agent/fix-chat-disconnect
lily/add-npc-memory-hook
agent/issue-42-terrain-render
```

### Using worktrees (recommended for agents)

```bash
git worktree add /tmp/my-task-worktree -b agent/my-task
cd /tmp/my-task-worktree
# ... do work ...
# When done, from the main checkout:
git worktree remove /tmp/my-task-worktree
```

Worktrees provide isolation — your changes can't accidentally conflict with the main checkout.

## 3. Implementation

### Scoping

- One logical change per branch/PR — do not bundle unrelated fixes
- If you discover adjacent issues, file new GitHub issues instead of fixing them in-place
- Do not modify files outside your task scope
- Do not add features beyond what was requested

### Code expectations

- Follow existing patterns in the directory you're working in
- TypeScript strict mode is enforced — no `any` unless unavoidable
- Write or update tests for behavioral changes
- Keep functions small (<50 lines), files focused (<800 lines)
- Use `@/` path aliases for imports from `src/`

## 4. Validation

Run these commands from the repo root before considering work complete:

```bash
# Required for all TypeScript changes
./b typecheck
./b test

# Required if you added new imports or files
./b circular

# Required if you changed dependencies
./b deps-check

# Required for C++/voxeloo changes
cd voxeloo && bazel test //...

# Required for documentation changes
cd docs && yarn build
```

All checks that were passing before your change must still pass after.

## 5. Committing

### Commit message format

```
<type>: <description>

<optional body explaining why, not what>
```

**Types:** `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`

### Examples

```
feat: add agent memory persistence to world state

Agents now store short-term memory as ECS components, allowing
memory to survive server restarts. Fixes #15.
```

```
fix: prevent chat disconnect on world rejoin

The WebSocket cleanup handler was firing before the new connection
was established, causing a race condition.
```

### Referencing issues

- `fixes #42` — automatically closes the issue when the PR merges
- `relates to #42` — links the issue without closing it

### Pre-commit checklist

- [ ] No secrets, API keys, or credentials in staged files
- [ ] No changes to files outside your task scope
- [ ] All validation commands pass
- [ ] No generated files (`src/gen/`) committed
- [ ] Commit message follows conventional format

## 6. Pull requests

### Creating a PR

```bash
# Push your branch
git push -u origin agent/my-task

# Create the PR (using gh CLI)
gh pr create --title "fix: description here" --body "..."
```

### PR body template

```markdown
## Summary

- What changed and why (1-3 bullets)

## Related issues

- Fixes #N / Relates to #N

## Test plan

- [ ] Ran `./b typecheck` — passing
- [ ] Ran `./b test` — passing
- [ ] Manual validation: <describe what you checked>

## Risks

- Any concerns or edge cases to watch for
```

### When to use draft PRs

- Work is in progress and you want early feedback
- You're blocked on a question and want to show context
- The change is large and you want incremental review

### PR scope rules

- One PR per logical change
- If a PR grows beyond ~400 lines of diff, consider splitting it
- Do not include formatting-only changes mixed with behavioral changes

## 7. Review and merge

- All PRs require at least one review before merging
- Address review feedback in new commits (don't force-push over review comments)
- Squash-merge is preferred for clean history
- Delete the branch after merging

## Agent-specific notes

### Reporting risks

If you encounter something uncertain during implementation, report it explicitly:

```
RISK: The UserSession type is used in 15 files. Changing its shape
may break callers I haven't found. Recommend grep for `UserSession`
across `src/` before merging.
```

### Avoiding scope creep

When you find adjacent problems:

1. Do NOT fix them in your current branch
2. File a new GitHub issue describing the problem
3. Reference the issue in your PR body as "discovered during this work"

### Recurring maintenance tasks

For agents running periodic maintenance (dependency updates, lint fixes, doc updates):

1. Create a dedicated branch per maintenance run
2. Keep each run focused on one type of maintenance
3. Include validation results in the PR body
4. Tag PRs with relevant labels
