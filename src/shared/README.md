# Shared Libraries Between Client/Server

Code that is used by both the client and server. This is the foundation layer — ECS types, math utilities, data structures, and shared game logic.

## Key areas

| Path               | Purpose                                                                  |
| ------------------ | ------------------------------------------------------------------------ |
| `ecs/`             | Entity Component System types and runtime (generated from `ecs/defs.py`) |
| `game/`            | Shared game logic (items, recipes, world rules)                          |
| `math/`            | Math utilities (vectors, matrices, noise, geometry)                      |
| `api/`             | Shared API type definitions                                              |
| `chat/`            | Shared chat types and utilities                                          |
| `bikkie/`          | Item/recipe definition types                                             |
| `data_structures/` | Reusable data structures                                                 |
| `ids.ts`           | Entity and type ID definitions                                           |
| `constants.ts`     | Game-wide constants                                                      |
| `loot_tables/`     | Drop rate and loot definitions                                           |

## Dependency rules

- **May import from:** other `@/shared/` modules only
- **Must NOT import from:** `@/client/`, `@/server/`, `@/pages/`
- This is the lowest layer. It must not depend on client or server code.
- Changes here affect both client and server — test thoroughly.
