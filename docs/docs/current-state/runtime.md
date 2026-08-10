---
sidebar_position: 3
---

# Runtime and Execution Model

This page describes how Biomes runs -- the process topology, data flow, storage, and build pipeline.

## Process Topology

A running Biomes instance consists of **~20 cooperating TypeScript processes** plus infrastructure services. The `./b` CLI launches them locally; in production they are deployed as separate Kubernetes pods.

```
Browser Client
   |
   |-- HTTPS --> [web]  (Next.js: pages, API routes, admin)
   |-- WSS ----> [sync] (WebSocket: real-time ECS updates)
   |-- HTTPS --> [oob]  (out-of-band entity lookups)
   |-- HTTPS --> [map]  (map tile serving)
   |-- HTTPS --> [chat] (chat messages)
   |
   +-- Three.js renderer + WASM voxel code (client-side)

Server-side services (not directly player-facing):
   [logic]   -- processes player events, writes ECS mutations
   [trigger]  -- listens to Firehose, drives quests/recipes/expiry
   [anima]   -- NPC AI ticks (sharded)
   [gaia_v2] -- natural simulation (lighting, growth, muck)
   [newton]  -- drop physics
   [task]    -- long-lived async jobs (Firestore)
   [sidefx]  -- side-effect processing
   [bikkie]  -- static content serving
   [spawn]   -- player spawn management
   [notify]  -- push notifications
   [backup]  -- world backup
   [balancer]-- shard/load management
   [bob]     -- build orchestration
   [camera]  -- screenshots
   [sink]    -- event persistence
   [ask]     -- query service
```

### Service Dependencies

When running locally, `./b <service-names>` starts only the listed services plus their transitive dependencies. The `web` service alone brings up a minimal playable stack. Adding `trigger`, `anima`, `gaia_v2`, etc. enables progressively more game systems.

## Data Flow

### ECS Event Loop (Implemented)

The central data path follows an ECS event-sourcing pattern:

1. **Client** sends an ECS event (e.g. "break block at position X") to the **logic** server.
2. **Logic** validates the event, applies event handlers (`src/server/logic/events/all.ts`), and writes ECS component mutations to **Redis**.
3. The **Redis Bridge** (`src/redis/`) detects mutations and publishes them to the **Firehose** (an event stream abstraction in `src/shared/firehose/`).
4. **Sync** servers, which maintain full or partial world replicas, consume Firehose events and push relevant ECS deltas to connected clients over WebSocket.
5. Downstream services (**trigger**, **sidefx**, **anima**, **gaia_v2**, etc.) also consume the Firehose to react to world changes.

### Inter-Service Communication (Implemented)

Services communicate via **zRPC** (`src/shared/zrpc/`), a custom gRPC-style RPC layer built on `@grpc/grpc-js`. It supports:

- Standard request/response calls
- Streaming (reliable streams with reconnection)
- MessagePort-based communication for in-process workers

### Client-Side Architecture (Implemented)

The browser client combines two rendering paradigms:

- **React 18** for UI (HUD, menus, admin panels, social pages)
- **Three.js** for the 3D voxel world

The **Resource System** (`src/shared/resources/`, `src/client/resources/`) bridges these two worlds with a dependency-injection framework that:

- Defines typed resource paths with lookup arguments
- Tracks dependencies between resources
- Notifies React when Three.js state changes, and vice versa
- Persists Three.js game state across React re-renders

WASM modules (compiled from `voxeloo/` C++ via Bazel) handle performance-critical voxel operations client-side.

## Storage

| Store | Role | Backing |
|-------|------|---------|
| **Redis 7** | Primary world state (ECS entities, terrain shards) | `src/redis/` |
| **Redis Bridge** | Publishes Redis mutations to the Firehose | Single-instance, part of `src/redis/` |
| **Firestore** | Auth, user accounts, long-lived task state | Firebase Admin SDK |
| **GCS (Google Cloud Storage)** | Asset storage, backups, data snapshots | `@google-cloud/storage` |
| **etcd** | Distributed locks for single-instance services (chat, bridge) | External service |
| **IndexedDB** | Client-side caching (via `idb` library) | Browser |

## Configuration

Configuration is layered, loaded from the first matching path:

1. `/biomes/biomes.config.yaml` -- production (mounted in K8s)
2. `./biomes.config.local.yaml` -- developer overrides (gitignored)
3. `./biomes.config.dev.yaml` -- committed dev defaults
4. `./deploy/k8/biomes.config.yaml` -- committed prod config (fallback)

Schema is defined in `src/server/shared/config.ts`. The config controls gameplay parameters (spawn limits, chat radius, gaia clock speed), WebSocket tuning, and service behavior.

## Build Pipeline

### `./b` CLI (Implemented)

The `./b` script is the primary developer interface. It is a Bash wrapper that invokes Python (`scripts/b/bootstrap.py`), which:

1. Checks prerequisites (Python >= 3.9, Git LFS, Bazel, rsync)
2. Installs Python dependencies if missing
3. Delegates to sub-commands (defined in `scripts/b/`)

Key sub-commands (inferred from `scripts/b/`):

| Command | Purpose |
|---------|---------|
| `./b data-snapshot run` | Pull data snapshot and start all services |
| `./b data-snapshot run-minimal` | Pull data snapshot and validate minimal local bring-up without requiring full asset completeness |
| `./b data-snapshot pull` | Download latest asset snapshot |
| `./b data-snapshot uninstall` | Remove local snapshot |
| `./b gen:ecs` | Regenerate ECS TypeScript from Python definitions |
| `./b galois build` | Build the Galois asset pipeline |
| `./b galois assets export` | Export game assets |

### Bazel (Implemented)

Bazel builds the C++ voxel engine (`voxeloo/`) and generates WASM/native bindings. The `BUILD.bazel` file in `voxeloo/` is the root of this build graph. Bazel utilities live in `src/bazel_utils/`.

### Next.js (Implemented)

The web frontend is a standard Next.js 13 app (`src/pages/` routing, `next.config.js` at root implied by `package.json`). Build/dev is handled by Next.js tooling under the hood, orchestrated by `./b`.

### CI (Implemented)

17 GitHub Actions workflows (`.github/workflows/`) cover:

- TypeScript CI and ESLint (`ts-ci.yml`, `ts-eslint-ci.yml`)
- C++ CI with clang checks (`cpp-ci.yml`)
- Bazel CI (`bazel-ci.yml`)
- Galois CI (`galois-ci.yml`)
- Redis CI (`redis-ci.yml`)
- LFS validation (`lfs-ci.yml`)
- Docs deployment (`docs-deploy.yml`)
- Merge CI (`merge-ci.yml`)

## ECS Code Generation (Implemented)

ECS schemas are defined in Python (`ecs/defs.py`) and code-generated into TypeScript:

```
ecs/defs.py  -->  ecs/gen.py  -->  src/shared/ecs/gen/
                                      components.ts  (~35k lines total)
                                      entities.ts
                                      events.ts
                                      types.ts
                                      selectors.ts
                                      json_serde.ts
                                      delta.ts
```

Run `./b gen:ecs` to regenerate after schema changes.
