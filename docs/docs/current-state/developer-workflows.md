---
sidebar_position: 4
---

# Developer Workflows

How to set up, run, and develop against the Biomes codebase as it exists today.

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Node.js | v20 (via nvm) | |
| Yarn | Latest v1 | `npm install -g yarn` |
| Python | >= 3.9, <= 3.10 | Virtual env recommended |
| Bazel | Latest (via Bazelisk) | `npm install -g @bazel/bazelisk` |
| Clang | >= 14 | For C++ voxel engine |
| Git LFS | Any | **Must be installed before clone** |
| Redis | 7.0.8 | Built from source (see setup guide) |
| RAM | **64 GB minimum** | Required for local development |

## First-Time Setup

```bash
# 1. Clone with LFS
git clone https://github.com/ill-inc/biomes-game.git
cd biomes-game
git lfs pull

# 2. Python environment (recommended)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Node dependencies
yarn install

# 4. Run
./b data-snapshot run
# Visit http://localhost:3000
```

The `data-snapshot run` command downloads a pre-built world snapshot (terrain, assets, Bikkie biscuits) and starts all services. First run takes significantly longer due to the snapshot download.

### Dev Container / Codespaces

The repo includes a `.devcontainer/` configuration. GitHub Codespaces with a **16-core / 64 GB** machine type is supported. Always use VS Code (not browser) to access `localhost:3000`.

## Running Subsets of Services

```bash
# Start only the web server (minimal playable stack)
./b web

# Start web + NPC AI + world simulation
./b web anima gaia_v2

# Start web + quest/trigger system
./b web trigger
```

Services auto-start their transitive dependencies. For example, `web` will start `sync` and `redis` automatically.

## Key Development Tasks

### Modifying ECS Schemas

1. Edit `ecs/defs.py` (Python schema definitions)
2. Run `./b gen:ecs`
3. Generated TypeScript appears in `src/shared/ecs/gen/`
4. Auto-formatted with Prettier

### Modifying Game Logic (Player Events)

Player-facing interactions are defined as ECS event handlers in:

```
src/server/logic/events/all.ts
```

Each handler receives an ECS event, validates it, and produces component mutations.

### Modifying Static Content (Bikkie)

1. Start the server locally (`./b data-snapshot run`)
2. Navigate to `http://localhost:3000/admin`
3. Use the Biscuit editor to modify items, blocks, quests, etc.
4. Changes are live immediately in the local environment
5. Schema changes: edit `src/shared/bikkie/schema/biomes.ts` and `src/shared/bikkie/schema/attributes.ts`

### Modifying the Voxel Engine

1. Edit C++ sources in `voxeloo/`
2. Build with Bazel: Bazel handles C++ compilation and WASM generation
3. JS/Python bindings are in `voxeloo/js_ext/` and `voxeloo/py_ext/`

### Working with the Asset Pipeline (Galois)

```bash
./b galois build          # Build the pipeline
./b galois assets export  # Export game assets
```

Terrain seed generation is done via Python notebooks in `src/galois/py/notebooks/`.

### Modifying NPC Behavior

NPC behaviors are defined as composable actions in `src/shared/npc/behavior/`:

| File | Behavior |
|------|----------|
| `meander.ts` | Random walking |
| `chase_attack.ts` | Chase and attack targets |
| `pathfinding.ts` | A* pathfinding |
| `return_home.ts` | Return to spawn point |
| `socialize.ts` | NPC social interactions |
| `swim.ts` / `fly.ts` / `drown.ts` | Movement modes |
| `damage_reaction.ts` | Respond to damage |

The Anima server (`src/server/anima/`) ticks NPC controllers, which execute these behaviors.

## Authentication (Local Dev)

Social login providers (Twitch, Discord, Google) require API keys not available locally. Use the **Dev Login** flow instead:

1. Go to `http://localhost:3000`
2. Click "Login" -> "Login with Dev"
3. Click "Create New Account"

## Configuration

Local config lives in `biomes.config.dev.yaml` (committed) or `biomes.config.local.yaml` (gitignored, for personal overrides). See `src/server/shared/config.ts` for the full schema.

Useful local-dev overrides:

```yaml
# Disable Discord webhooks (avoids startup errors without API keys)
discordHooksEnabled: false

# Speed up Gaia simulation
gaiaClockMultiplier: 20.0

# Reduce NPC count for performance
animaGlobalSpawnLimit: 100
```

## IDE Setup

VS Code is recommended. The `tsconfig.json` at root defines path aliases (`@/*` -> `src/*`), which VS Code resolves automatically.

## Asset Troubleshooting

If you see 404 errors for asset paths after updating:

```bash
./b data-snapshot uninstall
./b data-snapshot pull
```

## CI

Pull requests trigger the relevant subset of 17 CI workflows depending on which files changed. Key ones:

- `ts-ci.yml` -- TypeScript build and tests
- `cpp-ci.yml` -- C++ build with clang checks
- `galois-ci.yml` -- Asset pipeline tests
- `ts-eslint-ci.yml` -- Lint checks
