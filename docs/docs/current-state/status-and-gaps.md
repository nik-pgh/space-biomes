---
sidebar_position: 5
---

# Status and Gaps

This page contrasts the **current code reality** with the **OpenClaw-agent MMORPG direction** described in the README. It identifies what exists, what is partially built, and what is entirely aspirational.

## Summary

The Biomes codebase is a **fully functional voxel MMORPG** with a rich set of implemented game systems. The "OpenClaw-agent" framing in the README is a **vision statement** -- no agent-specific code exists in the repository today. The gap between the existing game engine and the stated agent-native goals is substantial but bounded: the engine already supports multiplayer, NPCs, quests, and a flexible ECS, which are all foundations that an agent layer could build on.

## Detailed Status

### 1. Agent Presence Layer

**README claims:** Stable identity and profile model for OpenClaw agents; spawn, session continuity, role/state synchronization.

| Aspect | Status | Evidence |
|--------|--------|----------|
| Player identity/profile model | **Implemented** (for human players) | Firebase auth, ECS player entities, `src/pages/auth/` |
| NPC identity/spawn | **Implemented** (for scripted NPCs) | `src/server/anima/`, `src/server/spawn/`, NPC ECS components |
| OpenClaw agent identity | **Aspirational** | No code references to "openclaw", "agent.presence", or agent-specific identity |
| Agent session continuity | **Aspirational** | No agent session management code exists |
| Agent role/state sync | **Aspirational** | No agent-specific state synchronization |

**Gap:** The existing NPC and player systems provide a foundation, but there is no agent-specific identity model, API, or session management. An agent would need a way to authenticate, maintain persistent identity, and resume sessions -- none of which exist.

### 2. Agent Memory + World State Integration

**README claims:** Short-term and long-term memory hooks; in-world memory artifacts (journals, logs, guild records).

| Aspect | Status | Evidence |
|--------|--------|----------|
| World state access | **Implemented** | ECS provides full world state; sync servers replicate it |
| NPC behavior state | **Implemented** (ephemeral) | `src/shared/npc/behavior/` -- tick-based, no persistent memory |
| Agent memory hooks | **Aspirational** | No memory abstraction, storage, or retrieval system for agents |
| In-world artifacts | **Aspirational** | No journal, log, or record entity types for agents |

**Gap:** NPCs have behavior trees but no persistent memory between sessions. The ECS could be extended with memory components, but nothing exists today.

### 3. Multiplayer Social Systems

**README claims:** Faction/guild mechanics for agents and humans; communication and coordination primitives.

| Aspect | Status | Evidence |
|--------|--------|----------|
| Real-time chat | **Implemented** | `src/server/chat/`, `src/shared/chat/`, configurable radius |
| Player interactions | **Implemented** | ECS events for trading, gifting, social actions |
| Groups/teams | **Partially implemented** | `src/pages/api/environment_group/` suggests group mechanics |
| Factions/guilds | **Aspirational** | No faction or guild entity types, membership, or governance code |
| Agent-to-agent coordination | **Aspirational** | No coordination primitives beyond existing chat |

**Gap:** Chat and basic social interactions work. Guild/faction systems would require new ECS components, UI, and server logic.

### 4. Questing and Economy Loops

**README claims:** Repeatable tasks, contracts, world events; resource flow supporting autonomous participation.

| Aspect | Status | Evidence |
|--------|--------|----------|
| Quest system | **Implemented** | `src/server/trigger/`, `src/shared/triggers/`, Bikkie quest definitions |
| Recipe/crafting system | **Implemented** | Trigger server unlocks recipes; Bikkie defines items |
| Item drops and loot | **Implemented** | `src/server/newton/`, loot tables in `src/shared/loot_tables/` |
| Economy (trading) | **Partially implemented** | Item attributes include `sellPrice`; trading events exist |
| Repeatable agent tasks | **Aspirational** | No contract or repeatable-task system designed for agent consumption |
| World events | **Inferred** | Trigger system could drive events, but no world-event framework found |

**Gap:** The quest and economy systems are the most complete foundation for agent interaction. An agent API that can query available quests, accept them, and report completion would bridge most of this gap.

### 5. Safety + Governance

**README claims:** Permission boundaries for agent actions; logging, moderation, and rollback-safe operations.

| Aspect | Status | Evidence |
|--------|--------|----------|
| Admin panel | **Implemented** | `src/pages/admin/`, extensive Bikkie editor |
| Server-side event validation | **Implemented** | Logic server validates all ECS events |
| World backup/restore | **Implemented** | `src/server/backup/` |
| Logging/metrics | **Implemented** | `prom-client` metrics, structured logging, Firehose event stream |
| Agent-specific permissions | **Aspirational** | No permission boundary system for agent actions |
| Agent behavior moderation | **Aspirational** | No agent-specific moderation or observability tools |
| Rollback per-agent | **Aspirational** | Backup is world-level, not agent-scoped |

**Gap:** The infrastructure for logging and backup exists. Agent-specific permission boundaries and per-agent rollback would be new systems.

## What Would Need to Be Built

Based on the gap analysis, the major new systems required for the OpenClaw-agent vision are:

### Must-Build (No Existing Foundation)

1. **Agent Authentication & Identity** -- An auth flow and ECS entity type for autonomous agents (distinct from human players and scripted NPCs).
2. **Agent Session Manager** -- Spawn, heartbeat, reconnection, and session persistence for long-running agents.
3. **Agent Memory Store** -- Persistent short-term and long-term memory, queryable by the agent, possibly backed by a new storage layer.
4. **Agent Permission System** -- Action-level permission boundaries (e.g., "this agent can break blocks but not trade").
5. **Agent API Surface** -- A stable API (REST or RPC) that agents use to observe the world, take actions, and receive events, decoupled from the browser client's WebSocket protocol.

### Can Extend (Foundation Exists)

6. **Agent Quest Integration** -- Extend the trigger/quest system with an API for agents to discover, accept, and complete quests.
7. **Agent Communication** -- Extend the chat system with structured message types for agent-to-agent and agent-to-human coordination.
8. **Faction/Guild System** -- New ECS components and server logic, but the ECS and admin tooling make this tractable.
9. **Agent Observability** -- Extend existing metrics and Firehose with agent-specific dashboards and moderation views.

## Documentation Gaps

The existing Docusaurus docs (`docs/docs/basics/`) cover:

- Local setup (thorough)
- Server architecture (good high-level overview)
- ECS (brief but functional)
- Bikkie (good, with screenshots)
- Admin panel (good)
- Terrain data model (detailed)
- Resource system (brief)

**Missing documentation:**

- No architecture decision records
- No API reference for `src/pages/api/` endpoints
- No guide for extending ECS with new component types
- No NPC/Anima behavior authoring guide
- No Galois asset pipeline walkthrough
- No deployment/operations guide
- No performance tuning guide
- No security model documentation

## Risk Assessment

| Risk | Severity | Notes |
|------|----------|-------|
| 64 GB RAM requirement limits contributor pool | Medium | Codespaces mitigates but is not free |
| No agent code exists; README may set incorrect expectations | High | Contributors expecting agent systems will find nothing |
| C++ voxel engine has no Rust code despite Rust build utils existing | Low | `src/bazel_utils/rust/` and `src/cayley/` suggest Rust was explored but `voxeloo/` is pure C++ |
| Firebase/GCP coupling may complicate self-hosting | Medium | Auth, storage, and secrets are GCP-specific |
| Next.js 13 is several major versions behind current | Low | Functional but will need upgrading eventually |
| `openai` dependency (v3) is very outdated | Low | Only one import; unclear if actively used |
