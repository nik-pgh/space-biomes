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

From repo root:

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

## Remaining completeness gaps

1. `buckets/biomes-static/` is still only a scaffold, not a populated asset mirror.
2. `buckets/biomes-bikkie/` is still empty, so runtime fetches for binary bikkie assets will still 404 later.
3. `backup.json` is only the minimal synthetic bikkie seed, with no ECS world entity payload, so Redis bootstrap may move to a later blocker after install succeeds.
