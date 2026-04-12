# HEARTBEAT_HANDOFF

## Top goal
Get local Biomes reconstruction bring-up working honestly from the reconstructed snapshot path, using the local snapshot flow instead of the old remote snapshot URL.

## Previous work
- Groundwork already merged into `dev`:
  - stable managed Python helper
  - local reconstructed snapshot seed
  - local snapshot directory install path via `BIOMES_SNAPSHOT_DIR`
  - minimal boot validation path via `./b data-snapshot run-minimal`
- Issue-loop progression:
  - #35 established the initial asset completeness gap: `0/2769` static assets present, first blocker `atlases/blocks`
  - #36 materialized 5 startup-critical assets and moved the blocker to `audio/applause`
  - #37 verified the blocker was still `audio/applause`, with `2764` assets still missing
  - #38 added `run-minimal`, so full static-asset completeness is no longer the first required gate for minimal bring-up verification
  - #39 is the next retry issue for verification through the new minimal path, and is still open / not yet completed

## What to do next
1. Retry bring-up through `./b data-snapshot run-minimal` under the corrected local runtime setup.
2. Make the retry honest: only mark success if the minimal boot is directly observed.
3. If the run fails, capture the next concrete blocker and either:
   - continue directly if it is small and local, or
   - use the `issue-worker-retry-loop` skill if the blockage is broad or decomposes cleanly into issue-sized work.
4. Resolve local port contention before the retry: port 3000 is occupied, and 3001 was also occupied last check by `openclaw-dashboard`, so clear 3001 or explicitly choose another acceptable fallback.

## Things the agent should know
- Local machine runtimes were corrected to Node 20 and managed Python 3.10.
- The old remote snapshot URL path should be bypassed by `BIOMES_SNAPSHOT_DIR` pointing at the local reconstructed snapshot directory.
- Use isolated worktrees for repo modifications.
- Close GitHub issues honestly, only when the stated issue is actually resolved.
- Do not claim boot success unless it was directly observed in the current session.
- The main open question is no longer full asset completion first; it is whether the new minimal path can boot far enough to establish the next real blocker or a genuine success.
