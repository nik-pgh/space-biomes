# Server-only Source

Game server subsystems. This code runs on the server and handles world simulation, persistence, NPC behavior, and game logic.

## Key directories

| Directory  | Purpose                                                          |
| ---------- | ---------------------------------------------------------------- |
| `logic/`   | Core game logic and world simulation rules                       |
| `anima/`   | NPC and agent animation/behavior systems                         |
| `chat/`    | Server-side chat and messaging                                   |
| `gaia_v2/` | World generation and terrain                                     |
| `spawn/`   | Entity spawning and lifecycle                                    |
| `sync/`    | Client-server state synchronization                              |
| `task/`    | Async task execution                                             |
| `trigger/` | Event triggers and hooks                                         |
| `web/`     | HTTP server and WebSocket handling                               |
| `bob/`     | Content pipeline ("Bob the builder")                             |
| `bikkie/`  | Item/recipe definition system                                    |
| `newton/`  | Physics simulation                                               |
| `shared/`  | Server-internal shared utilities (not the same as `src/shared/`) |

## Dependency rules

- **May import from:** `@/shared/`
- **Must NOT import from:** `@/client/`, `@/pages/`
- Client code must never appear here. If both client and server need something, put it in `src/shared/`.
