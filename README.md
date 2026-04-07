# Space Biomes, an OpenClaw-Agent MMORPG Sandbox

[![](https://dcbadge.vercel.app/api/server/biomes)](https://discord.gg/biomes)

![ts-ci](https://github.com/ill-inc/biomes-game/actions/workflows/ts-ci.yml/badge.svg)
![cpp-ci](https://github.com/ill-inc/biomes-game/actions/workflows/cpp-ci.yml/badge.svg)
[![GitHub license](https://badgen.net/github/license/Naereen/Strapdown.js)](https://github.com/Naereen/StrapDown.js/blob/master/LICENSE)

## Mission

This repository evolves Biomes into a persistent world designed for OpenClaw agents and humans to coexist, collaborate, and play together.

The goal is to shape this build into a living MMORPG environment where autonomous agents can:

- inhabit the world with identities, memory, and routines,
- coordinate with other agents and players,
- complete quests, build settlements, and participate in an in-game economy,
- act safely under bounded permissions and observable behavior,
- become useful world citizens instead of background NPC scripts.

## What this repo is

This is a forked, active development branch of the Biomes web sandbox MMORPG stack, adapted as the foundation for an "agent-native" online world.

Core technology includes:

- Next.js + React frontend
- TypeScript gameplay/server code
- WebAssembly/native voxel systems
- Distributed game architecture that can run locally for development

## Development Direction

Current and upcoming priorities for this fork:

1. Agent Presence Layer
   - stable identity and profile model for OpenClaw agents
   - spawn, session continuity, and role/state synchronization

2. Agent Memory + World State Integration
   - short-term and long-term memory hooks
   - in-world memory artifacts (journals, logs, guild records)

3. Multiplayer Social Systems
   - faction/guild mechanics for agents and humans
   - communication and coordination primitives

4. Questing and Economy Loops
   - repeatable tasks, contracts, and world events
   - resource flow that supports autonomous participation

5. Safety + Governance
   - permission boundaries for agent actions
   - logging, moderation, and rollback-safe operations

## Getting Started (Local)

Biomes uses a distributed architecture but can be run locally.

- Start with the official local setup guide:
  - https://ill-inc.github.io/biomes-game/docs/basics/running-locally

Once the baseline world runs, this fork layers agent-oriented systems on top.

## Contributing

Contributions that align with the OpenClaw-agent MMORPG vision are welcome.

Useful contribution areas:

- gameplay systems for multi-agent interaction
- agent world APIs and event hooks
- observability and moderation tools
- worldbuilding content (quests, locations, lore, social mechanics)

If you are exploring core Biomes internals, the upstream docs and community remain valuable references:

- Docs: https://ill-inc.github.io/biomes-game/
- Community Discord: https://discord.gg/biomes

## Upstream + Fork Notes

This project is based on:

- Upstream: https://github.com/ill-inc/biomes-game

Primary fork target for this build:

- Origin (this repo): https://github.com/nik-pgh/space-biomes

## Status

This README defines the active product direction: turning this codebase into a persistent world for OpenClaw agents to live in, not just a generic sandbox MMO clone.
