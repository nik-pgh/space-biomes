# Agent Operating Instructions

This file defines how autonomous coding agents should work in this repository. It applies to all agent types (Claude Code, Copilot, Codex, etc.).

For Claude Code-specific build commands and repo layout, see `CLAUDE.md`.

## Scope and boundaries

### You MAY

- Edit TypeScript source in `src/` (client, server, shared, pages)
- Edit C++ source in `voxeloo/` (if you understand Bazel builds)
- Edit ECS definitions in `ecs/defs.py` (then regenerate with `yarn gen:ecs`)
- Edit documentation in `docs/`
- Add or improve tests
- Fix lint/type errors
- Update markdown documentation and agent guidance files

### You MUST NOT

- Modify CI workflows (`.github/workflows/`) without explicit approval
- Modify Kubernetes manifests in `deploy/` without explicit approval
- Delete or rename files outside your assigned scope
- Commit secrets, API keys, or credentials
- Force-push to any branch
- Push directly to `main` — always use pull requests
- Modify generated files (`src/gen/`) by hand
- Change build infrastructure (`WORKSPACE.bazel`, `Cargo.Bazel.lock`, root `package.json` dependencies) without approval

### Ask before

- Adding new npm dependencies
- Creating new top-level directories
- Changing database schemas or ECS component definitions
- Modifying shared type definitions that affect many consumers
- Any change to authentication, permissions, or safety systems

## Workflow

### Starting work

1. Always work in a git worktree or feature branch, never directly on `main`
2. Read `CLAUDE.md` for build commands and repo orientation
3. Read the `AGENTS.md` in the directory you'll be working in
4. Run `./b typecheck` to confirm a clean starting state
5. Check open GitHub issues for context on your task

### Branch naming

```
<author>/<short-description>
```

Examples: `agent/fix-chat-disconnect`, `lily/add-npc-memory-hook`

### Making changes

1. Keep changes focused — one logical change per branch/PR
2. Do not touch unrelated files
3. Run validation before considering work complete:
   - `./b typecheck`
   - `./b test`
   - `./b circular` (if you added new imports)
4. Write or update tests for behavioral changes
5. If you break something, fix it before moving on

### Committing

Follow conventional commit format:

```
<type>: <description>

<optional body explaining why>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`

Reference GitHub issues when applicable: `fix: resolve chat disconnect on rejoin (fixes #42)`

### Pull requests

- Use draft PRs for work-in-progress
- PR title should be concise (<70 chars)
- PR body should explain what changed and why
- Include a test plan or validation steps
- Reference related issues with `fixes #N` or `relates to #N`
- See `CONTRIBUTING.md` for the full PR workflow

## Safety rules

1. **Never commit secrets.** Check staged files for `.env` values, API keys, tokens, or passwords before every commit.
2. **Never force-push.** If your branch has diverged, rebase or merge — don't overwrite.
3. **Preserve working state.** If `./b typecheck` or `./b test` passes before your change, it must pass after.
4. **Report risks.** If you're uncertain whether a change is safe, say so explicitly rather than guessing.
5. **Don't expand scope.** If you discover adjacent problems, file issues — don't fix them in the same PR unless they're blocking.

## Reporting

When finishing a task, report:

- What changed and why
- Files modified
- Validation commands run and their results
- Any risks, open questions, or follow-up work needed
- Commit hash if a commit was created

## Directory-specific guidance

Each major directory has its own `AGENTS.md` with constraints and common tasks specific to that area. Always read the local `AGENTS.md` before working in a directory.
