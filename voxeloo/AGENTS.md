# voxeloo/ — Agent Guide

This directory contains the C++ voxel engine and its WASM/Python bindings. It's built with Bazel and provides the low-level voxel, terrain, and geometry operations used by the game.

## Structure

| Path           | Purpose                                                |
| -------------- | ------------------------------------------------------ |
| `biomes/`      | Core biomes-specific C++ code                          |
| `common/`      | Shared C++ utilities (geometry, math, data structures) |
| `gaia/`        | World generation and terrain systems                   |
| `galois/`      | Asset processing (meshes, textures, blocks)            |
| `tensors/`     | Tensor/array operations for voxel data                 |
| `js_ext/`      | JavaScript/WASM bindings                               |
| `py_ext/`      | Python bindings                                        |
| `anima/`       | Animation system                                       |
| `mapping/`     | Coordinate mapping utilities                           |
| `gen/`         | Generated code                                         |
| `third_party/` | Vendored C++ dependencies                              |

## Build commands

All commands run from the `voxeloo/` directory:

```bash
# Build everything
bazel build //...

# Run all tests
bazel test //...

# Build WASM (run from repo root)
scripts/build_wasm.sh -t all

# Install Python extension (from repo root)
pip install ./voxeloo
```

## Code style

- Follows `.clang-format` (in this directory)
- Static analysis via `.clang-tidy`
- Validate formatting: `scripts/clang-format-checks.sh` (from repo root)

## Constraints

- **Requires Bazel** — install via `brew install bazelisk` (macOS) or see `README.md`
- **Do not modify `third_party/`** — vendored dependencies are pinned
- **Do not modify `BUILD.bazel` files** without understanding Bazel build rules
- Changes here can break WASM builds, which affect the entire game client
- C++ changes require running `bazel test //...` — TypeScript tests won't catch C++ bugs

## Common tasks

### Adding a new C++ source file

1. Create the `.hpp`/`.cpp` file in the appropriate subdirectory
2. Add it to the `BUILD.bazel` in that directory
3. Run `bazel build //...` to verify compilation
4. Run `bazel test //...` to verify tests pass

### Modifying WASM bindings

1. Edit binding code in `js_ext/`
2. Rebuild WASM: `scripts/build_wasm.sh -t all` (from repo root)
3. Run `./b typecheck` to verify TypeScript still compiles with new bindings
4. Run `./b test` for integration tests

## Validation

```bash
cd voxeloo
bazel build //...   # Must compile
bazel test //...    # Must pass
```
