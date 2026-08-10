# Issue #32 local reconstructed snapshot seed

This branch adds a concrete repo-local snapshot install path at:

```text
tmp/reconstructed-snapshot/
```

Layout:

```text
tmp/reconstructed-snapshot/
  backup.json
  buckets/
    biomes-static/
    biomes-bikkie/
```

## Why this exists

`./b data-snapshot pull` fails first on the dead upstream snapshot URL (`https://static.biomes.gg/biomes_data_snapshot.tar.gz`).

The smallest viable way to move retries past that blocker is to provide a local unpacked snapshot directory and point `BIOMES_SNAPSHOT_DIR` at it, because `scripts/b/data_snapshot.py` checks `BIOMES_SNAPSHOT_DIR` before any remote download.

## Seed contents

- `backup.json`: tiny version-2 backup with a decodable `bikkie` entry
- `buckets/biomes-static/`: placeholder directory only
- `buckets/biomes-bikkie/`: placeholder directory only

The backup seed came from the earlier local reconstruction attempt at `/private/tmp/space-biomes-reconstruction-attempt/snapshot_backup.json`.

## How to use it

For a repo-supported minimal bring-up path that does not require full
`biomes-static` completeness:

```bash
export BIOMES_SNAPSHOT_DIR="$PWD/tmp/reconstructed-snapshot"
./b data-snapshot run-minimal
```

Or through the Python bootstrap entrypoint:

```bash
./scripts/with_biomes_python.sh python ./scripts/b/bootstrap.py data-snapshot run-minimal
```

The default strict path is still:

```bash
./b data-snapshot run
```

That command still requires full asset completeness and will stop on missing
assets such as `audio/applause`.

If you only want to verify that snapshot install sources locally, without
starting the full stack, use:

```bash
export BIOMES_SNAPSHOT_DIR="$PWD/tmp/reconstructed-snapshot"
./b data-snapshot pull
```

Or, without `./b`, using the underlying Python entrypoint:

```bash
env PYTHONPATH=scripts:scripts/b \
  BIOMES_SNAPSHOT_DIR="$PWD/tmp/reconstructed-snapshot" \
  python3 tmp/validate_issue32_local_snapshot.py
```

## What this proves

This local directory is enough for snapshot installation to source inputs locally instead of attempting the dead upstream download URL.

`./b data-snapshot run-minimal` extends that into a supported bring-up path:
it installs the snapshot, warns on missing assets, and proceeds to Redis/web
startup so local boot can be validated without waiting on full `biomes-static`
 reconstruction.

## Remaining completeness gaps

1. `buckets/biomes-static/` is still only a scaffold, not a populated asset mirror.
2. `buckets/biomes-bikkie/` is still empty, so runtime fetches for binary bikkie assets will still 404 later.
3. `backup.json` is only the minimal synthetic bikkie seed, with no ECS world entity payload, so Redis bootstrap may move to a later blocker after install succeeds.
4. `run-minimal` is intentionally weaker validation than `run`: it proves minimal bring-up only, not that local asset serving is production-complete.
