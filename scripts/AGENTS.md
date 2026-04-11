# scripts/ — Agent Guide

This directory contains build scripts, the `./b` command system, and CI support utilities.

## Structure

| Path                     | Purpose                                                           |
| ------------------------ | ----------------------------------------------------------------- |
| `b/`                     | Python subcommands for the `./b` build tool                       |
| `b/bootstrap.py`         | Entry point — dispatches `./b <subcommand>`                       |
| `b/ts_deps.py`           | TypeScript dependency generation                                  |
| `b/galois.py`            | Galois asset pipeline commands                                    |
| `b/data_snapshot.py`     | Data snapshot management                                          |
| `node/`                  | Node.js-based build scripts (webpack configs, test runners, etc.) |
| `build_ecs.sh`           | ECS build script                                                  |
| `build_server.sh`        | Server build script                                               |
| `clang-format-checks.sh` | C++ formatting validation                                         |
| `clang-tidy-checks.sh`   | C++ static analysis                                               |

## The `./b` command

`./b` is the primary build tool. It's a Python script (`b/bootstrap.py`) that dispatches to subcommands:

```bash
./b typecheck        # Run TypeScript type checking
./b test             # Run tests
./b circular         # Check for circular dependencies
./b deps-check       # Validate dependency hygiene
./b ts-deps build    # Generate TypeScript dependencies from Bazel/ECS
./b galois build     # Build the Galois asset pipeline
./b data-snapshot run  # Run data snapshot
```

## Constraints

- **Do not modify `b/bootstrap.py`** — it's the critical entry point for all builds
- **Do not modify shell scripts** used by CI without understanding the CI context
- Scripts in `node/` are referenced by webpack configs and the build system — changes can break builds
- If adding a new `./b` subcommand, follow the pattern in existing `b/*.py` files

## Common tasks

### Understanding a build failure

1. Read the error output carefully — it usually names the failing file
2. Check which `./b` subcommand failed
3. Look at the corresponding `b/*.py` file to understand what it does
4. Fix the source code, not the build script (unless the build script has a genuine bug)

## Validation

The scripts themselves are validated indirectly by running the commands they implement:

```bash
./b typecheck
./b test
```
