# Claude Code / Coding Agent Guide

This file provides operational context for Claude Code and similar coding agents working in this repo.

## Repo overview

This is the Space Biomes codebase — a Biomes-derived open-world MMORPG being adapted for OpenClaw agent + human coexistence. The stack is Next.js + React frontend, TypeScript server/gameplay, C++/WASM voxel engine (voxeloo), and Python ECS code generation.

## Key directories

| Directory     | Purpose                                                       |
| ------------- | ------------------------------------------------------------- |
| `src/client/` | Browser-side game client (React components, renderer, input)  |
| `src/server/` | Game server subsystems (world sim, chat, physics, NPC AI)     |
| `src/shared/` | Code shared between client and server (ECS, types, utilities) |
| `src/pages/`  | Next.js pages and API routes                                  |
| `src/galois/` | Asset pipeline (geometry, textures, block definitions)        |
| `voxeloo/`    | C++/WASM voxel engine and native extensions                   |
| `ecs/`        | Python ECS code generation (`defs.py` → generated TypeScript) |
| `scripts/`    | Build tooling, `./b` subcommands, CI helpers                  |
| `deploy/`     | Kubernetes manifests and deployment config                    |
| `docs/`       | Docusaurus documentation site                                 |
| `.github/`    | CI workflows, issue templates, actions                        |

## Build system

The primary build tool is `./b` (a Python bootstrap script). All commands run from the repo root.

```bash
# Install dependencies
yarn install

# Generate TypeScript from ECS definitions
./b ts-deps build

# Type checking (the most common validation)
./b typecheck

# Run tests
./b test

# Check for circular dependencies
./b circular

# Check dependency hygiene
./b deps-check

# Build the voxeloo WASM module
scripts/build_wasm.sh -t all

# Build voxeloo C++ (requires Bazel)
cd voxeloo && bazel build //...

# Run voxeloo C++ tests
cd voxeloo && bazel test //...

# Regenerate ECS definitions
yarn gen:ecs
```

## CI validation

Pull requests trigger these GitHub Actions workflows based on changed paths:

- **ts-ci** (`src/`, `scripts/node/`, `yarn.lock`): typecheck, circular deps, deps-check, tests
- **cpp-ci** (`voxeloo/`): C++ build and tests via Bazel
- **galois-ci** (`src/galois/`): asset pipeline checks
- **docs-deploy** (`docs/`): documentation site build
- **redis-ci**: Redis integration tests
- **lfs-ci**: Git LFS validation

## Path aliases

TypeScript uses `@/` as a path alias for `src/`. Example: `import { foo } from "@/shared/utils"` resolves to `src/shared/utils`.

The `@/galois/*` alias maps to `src/galois/js/*`.

## Before committing

1. Run `./b typecheck` — must pass
2. Run `./b test` — must pass
3. Run `./b circular` — no new circular dependencies
4. Do not commit files matching `.gitignore` patterns (especially `src/gen/`, `node_modules/`, `.next/`, `bazel-*`)
5. Do not commit `.env.local` or any file containing secrets

## Code conventions

- TypeScript strict mode is enabled
- ESLint config is in `.eslintrc.js`, Prettier in `.prettierrc.js`
- Stylelint for CSS in `.stylelintrc.js`
- C++ follows clang-format (config in `voxeloo/.clang-format`)
- Python ECS code follows standard formatting (no black/ruff configured at repo level)

## Bootstrap environment variables

These env vars let you work around common local-launch blockers without editing scripts:

| Variable | Purpose | Example |
| --- | --- | --- |
| `BIOMES_PYTHON` | Override the Python interpreter used by `pip install ./voxeloo` and `pip install -r requirements.txt`. Useful when only `python3` (not `python`) is on PATH. | `export BIOMES_PYTHON=python3.10` |
| `BIOMES_SNAPSHOT_FILE` | Path to a pre-downloaded snapshot `.tar.gz`. Skips the download step entirely. | `export BIOMES_SNAPSHOT_FILE=~/biomes_data_snapshot.tar.gz` |
| `BIOMES_SNAPSHOT_URL` | Alternate URL for the snapshot download (replaces `static.biomes.gg`). | `export BIOMES_SNAPSHOT_URL=https://mirror.example.com/biomes_data_snapshot.tar.gz` |

## What NOT to do

- Do not modify generated files in `src/gen/` — they are produced by `./b ts-deps build`
- Do not modify `Cargo.Bazel.lock` or `WORKSPACE.bazel` without understanding Bazel dependency resolution
- Do not run `yarn gen:ecs` unless you intentionally changed `ecs/defs.py`
- Do not add new top-level directories without discussion
- Do not modify CI workflows (`.github/workflows/`) for cosmetic reasons

## Getting oriented in a new session

1. Read this file
2. Check `git status` and `git log --oneline -10` for recent context
3. Read `AGENTS.md` for workflow rules and boundaries
4. Read the `AGENTS.md` in whichever directory you'll be working in
5. Run `./b typecheck` to confirm the repo is in a clean state before making changes
