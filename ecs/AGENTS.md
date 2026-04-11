# ecs/ — Agent Guide

This directory contains the Entity Component System (ECS) definition and code generation pipeline. It produces TypeScript types and runtime code used throughout `src/shared/ecs/gen/`.

## Structure

| File         | Purpose                                                                                       |
| ------------ | --------------------------------------------------------------------------------------------- |
| `defs.py`    | Master ECS definition — all component types, entity types, and field definitions (~91K lines) |
| `ecs_ast.py` | AST representation for ECS definitions                                                        |
| `ts.py`      | TypeScript code generator                                                                     |
| `gen.py`     | Entry point for code generation                                                               |
| `templates/` | Code generation templates                                                                     |

## How it works

1. `defs.py` declares all ECS components and their field types in Python
2. `gen.py` parses the definitions and generates TypeScript files
3. Generated output goes to `src/shared/ecs/gen/` (gitignored)
4. Run via: `yarn gen:ecs` from repo root

## Common tasks

### Adding a new ECS component

1. Define the component in `defs.py` following existing patterns
2. Run `yarn gen:ecs` to regenerate TypeScript
3. Run `./b typecheck` to verify the generated code compiles
4. Update any systems in `src/` that should use the new component

### Modifying an existing component

1. Change the definition in `defs.py`
2. Regenerate: `yarn gen:ecs`
3. Fix all TypeScript consumers — the type checker will flag them
4. Run `./b typecheck` and `./b test`

## Constraints

- **Never hand-edit generated files** in `src/shared/ecs/gen/`
- Changes to `defs.py` affect the entire codebase. Type-check thoroughly.
- Removing or renaming a component field is a breaking change — check all consumers via grep
- This is Python code but it doesn't use the project's Python testing setup. Validate by regenerating and type-checking the output.

## Validation

```bash
yarn gen:ecs        # Regenerate
./b typecheck       # Verify output compiles
./b test            # Verify no runtime breakage
```
