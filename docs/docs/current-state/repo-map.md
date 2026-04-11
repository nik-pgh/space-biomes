---
sidebar_position: 2
---

# Repository Map

This page inventories every top-level directory and the major subsystems inside `src/`.

## Top-Level Directories

| Directory | Purpose | Status |
|-----------|---------|--------|
| `deploy/` | Kubernetes deployment manifests and config (`deploy/k8/`) | Implemented |
| `docs/` | Docusaurus documentation site (this site) | Implemented |
| `ecs/` | Python ECS schema definitions + code generator (`ecs/defs.py`, `ecs/gen.py`) | Implemented |
| `public/` | Static assets served by Next.js | Implemented |
| `scratch/` | Developer scratch/experiment area | Implemented |
| `scripts/` | `./b` CLI tool (Python), build helpers, deploy scripts | Implemented |
| `src/` | All application source code (client, server, shared) | Implemented |
| `templates/` | Project templates | Implemented |
| `voxeloo/` | C++ voxel engine, Bazel-built, with Python/JS bindings | Implemented |

## `src/` Subsystems

### `src/client/` -- Browser Client

| Subdirectory | Responsibility |
|--------------|---------------|
| `components/` | React UI components (HUD, menus, admin panels, game chrome) |
| `events/` | Client-side event handling |
| `game/` | Game loop initialization (`game.ts`, `init.ts`), WASM loading |
| `renderer/` | Three.js rendering pass pipeline (`pass_renderer.ts`) |
| `resources/` | Client-side resource system (see [Resources](../resources/overview)) |
| `styles/` | CSS / Tailwind styles |
| `util/` | Client utilities |

### `src/server/` -- Backend Microservices

Each service has a `main.ts` entry point and typically a `server.ts` that wires up the service.

| Service | Role | Notes |
|---------|------|-------|
| **web** | Next.js web server, API routes, admin site | Stateless; serves `src/pages/` |
| **sync** | WebSocket endpoint; maintains world replica, pushes ECS updates to clients | Core real-time path |
| **logic** | Processes player events (terrain edits, interactions) via ECS event handlers | `src/server/logic/events/all.ts` |
| **anima** | NPC AI controller, sharded across instances | Behavior trees in `src/shared/npc/behavior/` |
| **gaia_v2** | Natural world simulation (lighting, plant growth, farming, muck creep) | "Gaia" |
| **trigger** | Listens to Firehose; drives quest progression, recipe unlocks, expiry | |
| **chat** | Distributed chat with pub-sub feed, DM firehose events | Single-instance via distributed lock |
| **task** | Long-lived async tasks (Firestore-backed, crypto interactions) | |
| **newton** | Drop physics and pickup logic | |
| **map** | Periodic top-down world map tile generation | |
| **oob** | Out-of-band entity serving (distant data for clients) | Variant of sync |
| **bikkie** | Bikkie biscuit server (static content definitions) | |
| **bob** | Build/bundle orchestration service | |
| **camera** | Screenshot / camera service | |
| **spawn** | Player spawn management | |
| **notify** | Push notification dispatch | |
| **sidefx** | Side-effect processing from ECS changes | |
| **sink** | Event sink / persistence | |
| **ask** | Query service | |
| **backup** | World backup | |
| **balancer** | Load balancing / shard management | |
| **gizmo** | Developer tooling service | |
| **shim** | Compatibility shim for local development | |

### `src/shared/` -- Code Shared Between Client and Server

| Subdirectory | Responsibility |
|--------------|---------------|
| `ecs/` | ECS runtime + generated types (`gen/` -- ~35k lines) |
| `bikkie/` | Biscuit schema, attribute definitions, lookups |
| `npc/` | NPC types, behavior definitions, spawn events |
| `game/` | Game constants, terrain helpers, resource definitions |
| `zrpc/` | gRPC-style RPC layer ("zRPC") used for inter-service communication |
| `firehose/` | Event streaming abstraction (events pushed from Redis bridge) |
| `resources/` | Generic resource/dependency-injection system |
| `math/` | Vector, AABB, and spatial math utilities |
| `physics/` | Physics calculations shared between client prediction and server |
| `chat/` | Chat message types and serialization |
| `api/` | Shared API type definitions |
| `triggers/` | Trigger/quest definitions |
| `data_structures/` | Generic data structures |
| `wasm/` | WASM loading and type definitions |
| `util/` | General utilities (durations, logging, etc.) |

### `src/pages/` -- Next.js Routes

| Path | Content |
|------|---------|
| `pages/api/` | API endpoints (bikkie, chat, auth, social, bundles, etc.) |
| `pages/admin/` | Admin panel pages |
| `pages/auth/` | Authentication flows |
| `pages/at/`, `pages/g/`, `pages/p/`, `pages/u/` | Public profile / social pages |
| `pages/art/` | Art asset pages |

### `src/galois/` -- Asset Pipeline

| Subdirectory | Responsibility |
|--------------|---------------|
| `py/` | Python scripts and Jupyter notebooks for terrain seed generation |
| `js/` | JavaScript asset tooling |
| `scripts/` | Build scripts for Galois pipeline |
| `shaders/` | GLSL shader sources |
| `data/` | Asset data files |

### `voxeloo/` -- C++ Voxel Engine

| Subdirectory | Responsibility |
|--------------|---------------|
| `biomes/` | Core voxel operations for the Biomes world |
| `galois/` | C++ components of the Galois asset pipeline |
| `gaia/` | C++ components of the Gaia world simulation |
| `anima/` | C++ components of the NPC AI system |
| `tensors/` | Tensor/array operations for voxel data |
| `common/` | Shared C++ utilities |
| `mapping/` | Spatial mapping utilities |
| `gen/` | Generated C++ bindings |
| `js_ext/`, `py_ext/` | JavaScript and Python native extension bindings |

### Other `src/` Directories

| Directory | Purpose |
|-----------|---------|
| `src/cayley/` | Numerical/graphics library (Rust WASM, with notebooks and benchmarks) |
| `src/bazel_utils/` | Bazel build utilities for C++, Rust, and shaders |
| `src/benchmarks/` | Performance benchmarks |
| `src/email/` | Email template system (React Email) |
| `src/redis/` | Redis world store + bridge (maps Redis updates to Firehose) |
