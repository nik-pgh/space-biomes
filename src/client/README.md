# Client-only Source

Browser-side game client code. This runs in the player's browser and handles rendering, input, UI, and client-side game state.

## Key directories

| Directory     | Purpose                                           |
| ------------- | ------------------------------------------------- |
| `components/` | React UI components (HUD, menus, inventory, chat) |
| `renderer/`   | WebGL/Three.js rendering pipeline                 |
| `game/`       | Client-side game loop and state management        |
| `events/`     | Client event handling and input processing        |
| `resources/`  | Asset loading and resource management             |
| `styles/`     | CSS modules and global styles                     |
| `util/`       | Client-specific utilities                         |

## Dependency rules

- **May import from:** `@/shared/`, `@/galois/`
- **Must NOT import from:** `@/server/`, `@/pages/`
- Server code must never appear here. If both client and server need something, put it in `shared/`.
