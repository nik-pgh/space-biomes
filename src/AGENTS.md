# src/ — Agent Guide

This is the main TypeScript source directory. It contains the game client, server, shared libraries, Next.js pages, and specialized subsystems.

## Structure

| Directory      | Purpose                                                                                        |
| -------------- | ---------------------------------------------------------------------------------------------- |
| `client/`      | Browser-side game client — React components, WebGL renderer, input handling, game loop         |
| `server/`      | Game server — world simulation, NPC systems, chat, physics, spawning, persistence              |
| `shared/`      | Code used by both client and server — ECS definitions, types, math, utilities, data structures |
| `pages/`       | Next.js pages and API routes (the web application entry points)                                |
| `galois/`      | Asset pipeline — geometry processing, texture management, block definitions                    |
| `cayley/`      | Graph database integration                                                                     |
| `redis/`       | Redis client and caching utilities                                                             |
| `benchmarks/`  | Performance benchmarks                                                                         |
| `third-party/` | Vendored TypeScript dependencies and type definitions                                          |

## Import conventions

- Use `@/` path alias: `import { foo } from "@/shared/utils"`
- `@/galois/*` maps to `src/galois/js/*`
- Respect the dependency direction: `client/` → `shared/` ← `server/` (client and server depend on shared, not on each other)

## Constraints

- **Do not create circular dependencies.** Validate with `./b circular` after adding imports.
- **Do not import client code from server or vice versa.** Use `shared/` for common code.
- **Do not modify `src/gen/`** — it contains generated code from `./b ts-deps build`.
- **Do not modify `third-party/`** without understanding the vendoring setup.
- Test files live alongside source or in dedicated `test/` subdirectories.

## Validation

```bash
./b typecheck    # Type-check all TypeScript
./b test         # Run tests
./b circular     # Check for circular imports
./b deps-check   # Validate dependency graph
```

## Where to start for common tasks

| Task               | Start here                               |
| ------------------ | ---------------------------------------- |
| UI changes         | `client/components/`                     |
| Game mechanics     | `server/logic/` or `shared/game/`        |
| NPC/agent behavior | `server/anima/`                          |
| API endpoints      | `pages/api/`                             |
| Chat system        | `server/chat/` and `shared/chat/`        |
| World generation   | `server/gaia_v2/`                        |
| ECS components     | `shared/ecs/` (types from `ecs/defs.py`) |
| Rendering          | `client/renderer/`                       |
