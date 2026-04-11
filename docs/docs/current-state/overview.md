---
sidebar_position: 1
---

# Codebase Overview

> **Status key** used throughout this section:
>
> - **Implemented** -- code exists and is exercised by the local-dev or production path.
> - **Inferred** -- behavior deduced from code structure but not directly tested by the authors of this document.
> - **Aspirational** -- described in the README or roadmap but no corresponding implementation found in the tree.

## What Biomes Is Today

Biomes is a **browser-based, voxel-world MMORPG** built on:

| Layer | Technology | Key paths |
|-------|-----------|-----------|
| Frontend | Next.js 13 + React 18, Three.js renderer, WebAssembly | `src/client/`, `src/pages/` |
| Backend | ~20 TypeScript microservices communicating over gRPC (zRPC) and a Redis-backed Firehose | `src/server/` |
| Voxel engine | C++ (Bazel-built), exposed to TS/Python via WASM and native bindings | `voxeloo/` |
| Asset pipeline | Python notebooks + Bazel ("Galois") | `src/galois/` |
| Static content | "Bikkie" biscuit system with an in-browser admin editor | `src/shared/bikkie/` |
| Dynamic state | Custom Entity Component System (ECS), code-generated from Python definitions | `ecs/`, `src/shared/ecs/` |
| World sim | "Gaia" natural simulation (lighting, plant growth, farming, muck) | `src/server/gaia_v2/` |
| NPC AI | "Anima" -- sharded NPC controller with behavior-tree-style tick loop | `src/server/anima/`, `src/shared/npc/behavior/` |
| Storage | Redis 7 as primary world store; Firebase/Firestore for auth, tasks, and long-lived records | `src/redis/` |
| Deployment | Kubernetes manifests, GCP-oriented (GCS, PubSub, Secret Manager) | `deploy/k8/` |

The codebase is **monorepo-scale**: ~1,970 TypeScript/TSX files, ~200 C++ files, ~60 Python files, plus generated code under `src/shared/ecs/gen/` (~35 k lines).

## What the README Promises

The top-level README (rewritten in commit `a42e110`) reframes Biomes as an **"OpenClaw-agent MMORPG sandbox"** where autonomous agents coexist with human players. It describes five development directions:

1. Agent Presence Layer (identity, spawn, session continuity)
2. Agent Memory + World State Integration
3. Multiplayer Social Systems (factions, guilds)
4. Questing and Economy Loops
5. Safety + Governance (permissions, moderation, rollback)

**None of these agent-specific systems have corresponding code in the repository.** A grep for `openclaw`, `agent.presence`, `agent.memory`, and `agentLayer` returns only the README itself. The README is a statement of intent, not a description of current functionality.

## Scale at a Glance

| Metric | Value |
|--------|-------|
| Top-level directories | 9 (`deploy/`, `docs/`, `ecs/`, `public/`, `scratch/`, `scripts/`, `src/`, `templates/`, `voxeloo/`) |
| Server microservices | 20 (each has `main.ts` under `src/server/<name>/`) |
| TS/TSX source files | ~1,970 |
| C++/HPP source files | ~200 |
| Python source files | ~61 |
| Generated ECS code | ~35,000 lines (`src/shared/ecs/gen/`) |
| Dependencies (package.json) | ~110 runtime + ~90 dev |
| CI workflows | 17 (`.github/workflows/`) |
| Minimum RAM for local dev | 64 GB |
