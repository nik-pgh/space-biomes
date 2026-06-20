# HEARTBEAT_HANDOFF

Canonical handoff state for Space Biomes bring-up. Updated 2026-04-11, rechecked 2026-04-12 16:23 UTC.

## Repo baseline

Branch `dev` at commit `545a140` (merged PR #34: groundwork). Merged groundwork includes:

- Stable managed Python helper
- Local reconstructed snapshot seed
- Local snapshot directory install path via `BIOMES_SNAPSHOT_DIR`

## Verified issue status (nik-pgh/space-biomes)

| Issue | Title / scope | Status | Notes |
|-------|--------------|--------|-------|
| #32 | Assemble and use a local reconstructed snapshot instead of the dead upstream URL | **CLOSED** | Landed. |
| #38 | Minimal boot path (`run-minimal`) | **OPEN** | Published as PR #40, currently blocked by failing galois CI. |
| #39 | Retry bring-up through the minimal path | **OPEN** | Still blocked on #38 merging. |
| #41 | Fix galois CI pip-install failure under Python 3.12 for PR validation | **OPEN** | Implemented in PR #42, not merged yet. |
| #43 | Investigate hung export-ci after Python 3.11 galois fix validation | **OPEN** | Implemented in PR #44, not merged yet. |
| #45 | Investigate long-running `check-assets-uploaded-ci` after `export-ci` hang fix | **OPEN** | Investigation completed and commented. Remaining work is the unresolved shared CI setup hang and optional timeout mitigation publication. |
| #46 | Investigate Bazel `rustfmt` shared-library failure on PR #44 | **CLOSED** | Investigation completed and commented. The concrete next blocker is tracked in #47. |
| #47 | Fix Linux `bazel-ci` compile failure in `voxeloo/common/utils.hpp` | **OPEN** | Implemented and published as PR #48. `bazel-ci` is now green on PR #48, but the PR is still blocked by unrelated galois failures and new `cpp-ci` clang-format drift. |
| #49 | Stabilize `cpp-ci` clang-format version on `ubuntu-latest` | **OPEN** | Implemented and published as PR #50. Rechecked: still valid, but blocked behind PR #52 and external Git LFS restoration. |
| #51 | Restore Git LFS access for CI after budget exhaustion | **OPEN** | Investigated and published as mitigation PR #52. Root cause still includes external Git LFS budget exhaustion. |

## Issue #38, local worktree status

Worktree: `/private/tmp/space-biomes-issue-38`

The implementation adds:

- `./b data-snapshot run-minimal`, a minimal boot validation subcommand
- `scripts/b/data_snapshot_test.py`, unit tests for the data-snapshot commands
- Documentation updates

### Verified local state

- Branch: `lily/space-biomes-issue-38`
- Working tree: clean
- Local commit created: `1cf89a4` (`feat: add minimal local boot validation path (relates to #38)`)
- Branch pushed to origin: `origin/lily/space-biomes-issue-38`
- PR opened: `#40` <https://github.com/nik-pgh/space-biomes/pull/40>

### Validation evidence (rerun after cleanup)

**Tests pass (3/3):**
```
./scripts/with_biomes_python.sh python ./scripts/b/data_snapshot_test.py  ->  OK (3 tests)
```

**`run-minimal` is registered:**
```
PYTHONPATH=scripts/b ./scripts/with_biomes_python.sh python -c \
  "import b; print(sorted(b.data_snapshot_commands.commands.keys()))"
```
Output includes `run-minimal` in the command list.

**Worktree hygiene:**
- Accidental `.biomes/` artifacts were removed from the issue-38 worktree.
- Validation used a venv outside the worktree so the branch stayed clean.

### Why #38 is still OPEN

The implementation is now committed locally and published as PR #40, but it has not been merged into `dev` yet. Do not close #38 until the PR lands.

## Current blocker wave

PR #40 is **not** waiting on feature logic anymore. It is blocked by failing galois CI in run `24298789942`.

### Verified CI failure

Failing jobs:
- `export-ci`
- `check-assets-uploaded-ci`

Failure point in both jobs:
- `pip install -r requirements.txt`

Observed error:
- `ModuleNotFoundError: No module named 'distutils'`

Observed environment:
- GitHub Actions Python 3.12 during pip build backend setup

### Issue #41 follow-up

A focused unblock issue was created:
- `#41` <https://github.com/nik-pgh/space-biomes/issues/41>

The fix was implemented in an isolated worktree:
- worktree: `/private/tmp/space-biomes-issue-41`
- branch: `lily/space-biomes-issue-41`
- local commit: `8393f1e` (`fix: pin Python 3.11 in galois-ci to resolve distutils breakage (#41)`)
- branch pushed to origin: `origin/lily/space-biomes-issue-41`
- PR opened: `#42` <https://github.com/nik-pgh/space-biomes/pull/42>

Fix summary:
- pins `actions/setup-python@v5` with Python `3.11` in all three `galois-ci` jobs
- scope is limited to `.github/workflows/galois-ci.yml`
- intent is to move CI past the current Python 3.12 / `distutils` failure

## Issue #43 follow-up

The hung `export-ci` job was investigated in isolated worktree `/private/tmp/space-biomes-issue-43`.

### Verified local result

- Branch: `lily/space-biomes-issue-43`
- Working tree: clean
- Local commit created: `00d8879` (`fix: prevent export-ci hang when Python asset builder exits unexpectedly`)
- Branch pushed to origin: `origin/lily/space-biomes-issue-43`
- PR opened: `#44` <https://github.com/nik-pgh/space-biomes/pull/44>

### Worker findings

The worker identified a real hang path in the Node asset server glue:

- `BatchAssetServer.build()` waited for a readline `line` event from the Python subprocess
- if the Python subprocess exited without emitting a result line, the Promise never settled
- that left `export-ci` hanging until the GitHub Actions job timeout instead of surfacing the actual failure

Implemented fix summary:

- adds subprocess-exit / stream-close handling in `src/galois/js/server/server.ts`
- propagates publish-script failures via process exit in `src/galois/js/publish/scripts/publish.ts`

### Validation evidence

Passed in the issue-43 worktree:

- `npx tsc --noEmit --incremental`
- `./b test --path 'src/galois/**/test/*.ts'`  ->  18/18 passing

### What PR #44 has proved in CI so far

As of 2026-04-12 12:04 UTC, PR `#44` is still open, non-draft, mergeable, and `UNSTABLE`.

Verified galois state on PR `#44`:

- `export-ci` has completed with failure in the galois run after 8m13s
- the failed step is still `pip install`
- `gh run view 24304039071` now shows `export-ci` ending with `Process completed with exit code 2`
- `check-assets-uploaded-ci` is still in progress in that same galois run more than an hour after the run started
- GitHub still is not exposing failed-step logs for the completed `export-ci` job because the overall run `24304039071` remains in progress
- the previously observed improvement still holds: the original `export-ci` hang is no longer the visible outcome, and the job now surfaces failure instead of stalling for hours

A separate PR-44 check is also failing:

- `bazel-ci` failed in 14m2s
- failed logs show `bazel test --test_output=errors //...` hitting a Rust shared-library/toolchain problem while executing genrule `//src/cayley/impl:gen_ops`
- observed stderr includes `rustfmt: error while loading shared libraries: librustc_driver-796e47691512e4e9.so: cannot open shared object file`
- the Bazel summary reported `//voxeloo/common:utils_test FAILED TO BUILD`

Those are now being treated as two separate blocker tracks on PR `#44`.

### Best current hypothesis beyond the hang

The worker reported a likely underlying Python-side failure after the hang is removed:

- CI may be failing while installing or importing `voxeloo`
- one plausible cause is use of removed pip `--install-option` behavior in the cached pip install path

Treat that as a hypothesis, not a verified blocker, until PR #44 or a rerun exposes it directly in CI.

## Issue #45 follow-up

Issue `#45` was investigated in isolated worktree `/private/tmp/space-biomes-issue-45`.

### Verified local result

- Branch: `lily/space-biomes-issue-45`
- Working tree: clean
- Local commit created: `7479dd7` (`ci: bound galois job hangs with timeouts`)
- Branch has **not** been pushed yet
- GitHub issue `#45` was updated with the investigation result and left open

### Worker findings

The long-running `check-assets-uploaded-ci` state on PR `#44` does **not** appear to be a second hang in the asset-check logic.

- in run `24304039071`, `check-assets-uploaded-ci` never reached bazel, pip, ts build, or `./b galois assets check-assets-published`
- it remained much earlier in the shared `yarn install` setup path
- in the same run, `export-ci` completed `yarn install` and `bazel setup`, then failed fast at `pip install`
- this supports the current read that PR `#44` fixed the original export hang path, while the still-running check job is a separate shared CI setup/install hang or flake

Mitigation prepared locally:

- `.github/workflows/galois-ci.yml` updated to add `timeout-minutes: 30` to the three galois jobs
- this is a mitigation, not a root-cause fix for the shared install/setup hang

## Issue #46 and #47 follow-up

Issue `#46` was investigated in isolated worktree `/private/tmp/space-biomes-issue-46`.

### Verified local result

- Branch: `lily/space-biomes-issue-46`
- Working tree: clean
- No code changes were made
- GitHub issue `#46` was commented and then honestly closed
- New follow-up issue created: `#47` <https://github.com/nik-pgh/space-biomes/issues/47>

### Worker findings

The PR-44 `bazel-ci` failure does **not** look like a regression from the issue-43 patch.

- PR `#44` changes only `src/galois/js/server/server.ts` and `src/galois/js/publish/scripts/publish.ts`
- the `rustfmt` / `librustc_driver` problem around `//src/cayley/impl:gen_ops` reproduces on the pre-patch tree too, so it appears to be pre-existing toolchain/package noise
- the actual fatal GitHub Actions failure in `bazel-ci` is separate: `//voxeloo/common:utils_test FAILED TO BUILD`
- the worker traced that fatal failure to Linux CI seeing `voxeloo/common/utils.hpp` use `uint32_t` without a visible declaration

Treat issue `#47` as the concrete next Bazel blocker. Treat the Rust toolchain `rustfmt` loader problem as real but nonfatal noise for this specific PR-44 failure.

## Issue #47 follow-up

Issue `#47` was implemented in fresh isolated worktree `/private/tmp/space-biomes-issue-47`.

### Verified local state

- Branch: `lily/space-biomes-issue-47`
- Worktree: `/private/tmp/space-biomes-issue-47`
- Local fix was first committed as `46b155f`, then branch history was rebuilt on top of `origin/dev`
- Current branch head: `f7948e3` (`fix: add missing <cstdint> include in voxeloo/common/utils.hpp (fixes #47)`)
- Branch pushed to origin: `origin/lily/space-biomes-issue-47`
- PR opened: `#48` <https://github.com/nik-pgh/space-biomes/pull/48>
- GitHub issue `#47` was updated with the local validation result, PR link, and the branch-rebuild note

### Validation evidence

Passed in the issue-47 worktree:

- `bazel build //voxeloo/common:utils_test`
- `bazel test //voxeloo/common:utils_test` -> PASSED

### Worker findings

The fix is the narrow, standard correction for the verified fatal CI symptom.

- `voxeloo/common/utils.hpp` used `uint32_t` without including `<cstdint>`
- adding `#include <cstdint>` is consistent with other headers in `voxeloo/common/`
- local macOS validation passed cleanly
- PR `#48` later confirmed the fix in CI with a passing `bazel-ci`
- issue `#47` remains open only because PR `#48` is still blocked by unrelated required checks and has not landed yet

## Issue #49 follow-up

Issue `#49` was created after rechecking PR `#48`.

### Verified finding

- PR `#48` head `f7948e3` now has `bazel-ci` **passing**
- the same PR still fails `export-ci` and `check-assets-uploaded-ci` with the already-tracked Python 3.12 / `distutils` problem
- `cpp-ci` / `clang-format` failed on both:
  - untouched file `voxeloo/js_ext/galois.hpp`
  - touched file `voxeloo/common/utils.hpp`
- local `scripts/clang-format-checks.sh -c` passes with `clang-format 15.0.7`
- reproducing with clang-format `18.1.8` yields the same diffs CI reported
- root cause is that `.github/workflows/cpp-ci.yml` ran `scripts/clang-format-checks.sh -c` on `ubuntu-latest` without pinning a clang-format version

### Verified local result

- worktree: `/private/tmp/space-biomes-issue-49`
- branch: `lily/space-biomes-issue-49`
- local commit: `efefbd3` (`fix: pin clang-format to v15.0.7 in cpp-ci workflow`)
- branch pushed to origin: `origin/lily/space-biomes-issue-49`
- PR opened: `#50` <https://github.com/nik-pgh/space-biomes/pull/50>
- GitHub issue `#49` was updated with the reproduction result and PR link

### Fix summary

- adds `pipx install clang-format==15.0.7` to `.github/workflows/cpp-ci.yml` before running the formatter check
- keeps CI aligned with the formatter version that currently passes locally
- avoids unrelated PR failures from `ubuntu-latest` image drift until the repo intentionally reformats to a newer clang-format version

### Current PR state

- PR `#50` is open, non-draft, mergeable, and `UNSTABLE`
- both `clang-format` checks are now green on PR `#50`
- other relevant code-path checks on PR `#50` are also green, including `export-ci`, `js-ci`, `bazel-ci`, `ts-ci`, and `redis-ci`
- the remaining red check is `lfs-ci`
- failed run `24308217385` shows `git lfs pull` failing with:
  - `This repository exceeded its LFS budget. The account responsible for the budget should increase it to restore access.`
- issue `#49` was updated with this verification and remains open only because PR `#50` has not landed yet

## Issue #51 follow-up

Issue `#51` was created after rechecking PR `#50`.

### Verified current evidence

- PR `#50` is not blocked by the clang-format fix anymore
- `lfs-ci` failed in run `24308217385`
- failed step: `git lfs pull`
- observed error from GitHub Actions log:
  - `batch response: This repository exceeded its LFS budget. The account responsible for the budget should increase it to restore access.`
- this is a repo-level operational blocker, not a branch-specific code regression in PR `#50`

### Verified local result

- worktree: `/private/tmp/space-biomes-issue-51`
- branch: `lily/space-biomes-issue-51`
- local commit: `95fc3c4` (`ci: scope lfs-ci to LFS-relevant paths only`)
- branch pushed to origin: `origin/lily/space-biomes-issue-51`
- PR opened: `#52` <https://github.com/nik-pgh/space-biomes/pull/52>
- GitHub issue `#51` was updated with the investigation result, PR link, and the immediate follow-up finding

### Worker findings

There is a narrow honest in-repo mitigation, but it does not remove the external dependency.

- `lfs-ci` was running on every pull request even when the PR touched no LFS-managed content
- that made unrelated PRs like `#50` fail at `git lfs pull` for no relevant LFS-integrity signal
- PR `#52` scopes `lfs-ci` to LFS-relevant paths only:
  - all LFS-managed extensions from `.gitattributes`
  - `scratch/alpha_terrain.json`
  - `.gitattributes`
  - `.github/actions/cached-lfs-pull/**`
  - `.github/workflows/lfs-ci.yml`
- this is an honest mitigation for unrelated PRs during LFS budget exhaustion
- it does **not** fix the root cause: PRs that actually touch LFS-managed files still require external Git LFS budget/admin restoration

### Current PR state

- PR `#52` is open, non-draft, mergeable, and `UNSTABLE`
- because PR `#52` modifies `.github/workflows/lfs-ci.yml`, it still legitimately triggers `lfs-ci`
- PR-52 run `24309400453` failed at `git lfs pull` with the same repo-level Git LFS budget error
- so the honest current read is:
  - there **is** an in-repo mitigation for unrelated PRs
  - but merging that mitigation still requires the external Git LFS budget/admin unblock first, because the mitigation PR itself must run the LFS check

## Blockers and risks

- **PR #40 is still blocked on the galois CI chain being healthy.**
- PR `#42` remains open, non-draft, and mergeable. Its old run `24299394846` is no longer literally stuck: `export-ci` was eventually marked `CANCELLED` at 2026-04-12 11:23:47 UTC, while `check-assets-uploaded-ci` remains failed.
- PR `#44` remains the active unblock attempt for the hung `export-ci` state discovered on PR `#42`.
- Last verified PR `#44` state at 2026-04-12 12:04 UTC: open, non-draft, mergeable, `mergeStateStatus=UNSTABLE`.
- On PR `#44`, `export-ci` is now failing instead of hanging, but `check-assets-uploaded-ci` still appears long-running and the overall galois run `24304039071` is still in progress.
- GitHub still is not exposing failed-step logs for the completed PR-44 `export-ci` job while that overall galois run remains in progress.
- Issue `#45` clarified that the long-running PR-44 check job is currently best understood as a shared CI setup/install hang around `yarn install`, not a hang in the asset-check logic itself.
- Issue `#47` is now implemented as PR `#48`, which is the concrete Bazel blocker fix surfaced by the issue-46 investigation. PR `#44` should not be treated as blocked because its own diff broke Bazel.
- PR `#48` initially included the local handoff commit because the worktree was created from local `dev`; that was corrected by rebuilding the branch on top of `origin/dev`.
- Recheck at 2026-04-12 13:37 UTC: PR `#48` now has `bazel-ci` **green**, confirming the immediate Linux compile fix, but it is still red overall because:
  - `export-ci` and `check-assets-uploaded-ci` fail with the already-tracked Python 3.12 / `distutils` problem on base `dev`
  - `cpp-ci` / `clang-format` failed on an untouched file plus the touched header due to formatter-version drift between local clang-format 15.0.7 and `ubuntu-latest`
- Issue `#49` now has a narrow fix published as PR `#50`, which pins clang-format `15.0.7` in `cpp-ci`.
- Recheck at 2026-04-12 14:18 UTC: the PR-50 clang-format fix itself is green, but PR `#50` is blocked by repo-level `lfs-ci` failure caused by exhausted Git LFS budget.
- Issue `#51` now has a mitigation published as PR `#52`, which scopes `lfs-ci` to LFS-relevant paths only.
- Recheck at 2026-04-12 14:53 UTC: PR `#52` confirms the mitigation is correct in principle, but it still cannot land until external Git LFS budget/admin access is restored, because the mitigation PR itself legitimately triggers `lfs-ci`.
- Recheck at 2026-04-12 15:23 UTC: no material state change since the previous pass. PR `#52` is still red only on `lfs-ci`, PR `#50` is still red only on `lfs-ci`, and recent `lfs-ci` history continues to show the repo-level LFS budget outage as the first blocker.
- Recheck at 2026-04-12 15:53 UTC: still no material state change. PR `#52` remains blocked only by `lfs-ci`, PR `#50` remains blocked only by `lfs-ci`, and recent `lfs-ci` history still shows the same repo-level Git LFS budget failure as the first blocker.
- Recheck at 2026-04-12 16:23 UTC: still no material state change. PR `#52` remains blocked only by `lfs-ci`, PR `#50` remains blocked only by `lfs-ci`, and recent `lfs-ci` history still shows the same repo-level Git LFS budget failure as the first blocker.
- PR `#50` remains the first merge needed to make PR `#48` honestly pass its current formatter gate, but in practice the current merge order is: restore/clear LFS access enough to land PR `#52`, then rerun/land PR `#50`, then reassess PR `#48`.
- The Python 3.11 pin in PR `#42` clearly moved the blocker, because `js-ci` now passes and the old Python 3.12 / `distutils` failure is no longer the only observed outcome.
- Issue `#43` should remain open until PR `#44` lands.
- Issue `#41` should remain open until PR `#42` lands or is clearly superseded.
- Nothing downstream (#39) should proceed until `run-minimal` is merged.
- Full static-asset completeness is not required for the minimal path, but the actual boot may surface new blockers once executed.

## Recommended next step

1. **Restore Git LFS budget/admin access enough for `git lfs pull` to work again**, then merge PR `#52` and honestly keep or close issue `#51` based on whether the external outage is still considered active.
2. After PR `#52` lands, **rerun/reassess PR `#50`**. Merge it once clean, then honestly close issue `#49`.
3. After PR `#50` lands, **reassess PR `#48`**. Keep issue `#47` open until PR `#48` actually lands.
4. In parallel with that reassessment, keep treating the PR-48 galois reds as the already-tracked Python 3.12 / `distutils` blocker chain (`#41` / PR `#42`, then `#43` / PR `#44`).
5. **Decide whether to publish local commit `7479dd7` from issue `#45`** as a small CI-hardening PR. It bounds long galois hangs but does not fix the underlying shared setup/install flake.
6. **Check PR `#44` again if run `24304039071` ever completes**, and capture the exact failed-step logs for `export-ci` / `check-assets-uploaded-ci` if GitHub starts exposing them.
7. After PR `#52`, PR `#50`, PR `#48`, PR `#44`, and PR `#42` are honestly landable, **re-run or re-check PR `#40`** and merge it if clean.
8. **Honestly close issues `#51`, `#49`, `#47`, `#43`, `#41`, and `#38` only when their blockers or PRs have actually been cleared/landed.**
9. **Execute issue `#39`**: retry bring-up through `./b data-snapshot run-minimal` using the landed minimal path. Only mark success if boot is directly observed.
