# Biomes Local Boot Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the repo's local Biomes startup path reproducible and less brittle with small fixes only.

**Architecture:** Keep the existing `./b` launcher as the entrypoint, repair the stale service aliasing inside `scripts/b/b.py`, make Python helper scripts reuse the interpreter that launched `./b`, and make `segfault-handler` optional at runtime so missing native builds do not crash local startup. Document the supported local path as an empty-bootstrap, local-Redis flow instead of relying on the currently brittle snapshot bootstrap path.

**Tech Stack:** Python launcher scripts, TypeScript server bootstrap, Mocha/ts-node tests, unittest for Python, Markdown docs.

---

### Task 1: Add failing tests for the launcher and Python interpreter path

**Files:**
- Create: `scripts/b/test/test_local_boot.py`
- Modify: `scripts/b/b.py`
- Modify: `scripts/b/pip_install_voxeloo.py`

- [ ] **Step 1: Write the failing Python test file**

```python
import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

import b
import pip_install_voxeloo


class LauncherAliasTests(unittest.TestCase):
    def test_dev_alias_uses_gaia_service_name(self):
        expanded = b.expand_targets(["dev"])
        self.assertIn("gaia", expanded)
        self.assertNotIn("gaia_v2", expanded)

    def test_legacy_gaia_v2_alias_maps_to_gaia(self):
        self.assertEqual(b.expand_targets(["gaia_v2"]), ["gaia"])

    def test_local_alias_matches_supported_local_services(self):
        self.assertEqual(
            set(b.expand_targets(["local"])),
            {"logic", "chat", "map", "gaia", "web", "trigger", "task"},
        )


class PythonExecutableTests(unittest.TestCase):
    def test_prefers_explicit_python_override(self):
        with mock.patch.dict("os.environ", {"PYTHON": "/tmp/custom-python"}):
            self.assertEqual(
                pip_install_voxeloo.python_executable(), "/tmp/custom-python"
            )
```

- [ ] **Step 2: Run the Python test file to verify it fails**

Run: `python3 -m unittest discover -s scripts/b/test -p 'test_*.py'`
Expected: FAIL because `gaia_v2` still appears in launcher aliases and `python_executable()` does not exist yet.

- [ ] **Step 3: Implement the minimal launcher and interpreter changes**

```python
TARGET_ALIASES = {
    "dev": ["logic", "chat", "map", "gaia", "web", "trigger", "task"],
    "gaia_v2": ["gaia"],
    "local": ["logic", "chat", "map", "gaia", "web", "trigger", "task"],
    "all": list(ALL_SERVERS.keys()),
}


def python_executable():
    return os.environ.get("PYTHON") or sys.executable or shutil.which("python3") or "python3"
```

- [ ] **Step 4: Re-run the Python tests to verify they pass**

Run: `python3 -m unittest discover -s scripts/b/test -p 'test_*.py'`
Expected: PASS.

### Task 2: Add a failing TypeScript test for missing `segfault-handler`

**Files:**
- Create: `src/server/shared/test/process.test.ts`
- Modify: `src/server/shared/process.ts`

- [ ] **Step 1: Write the failing TypeScript test**

```typescript
import { log } from "@/shared/logging";
import assert from "assert";
import Module from "module";
import sinon from "sinon";

describe("handleProcessIssues", () => {
  it("does not crash when segfault-handler is unavailable", () => {
    const warn = sinon.stub(log, "warn");
    const originalLoad = Module._load;
    sinon.stub(Module, "_load").callsFake(((request, parent, isMain) => {
      if (request === "segfault-handler") {
        const error = new Error("missing");
        (error as NodeJS.ErrnoException).code = "MODULE_NOT_FOUND";
        throw error;
      }
      return originalLoad(request, parent, isMain);
    }) as typeof Module._load);

    const { handleProcessIssues } = require("@/server/shared/process");
    assert.doesNotThrow(() => handleProcessIssues());
    assert.ok(warn.called);
  });
});
```

- [ ] **Step 2: Run the TypeScript test to verify it fails**

Run: `./b test -p src/server/shared/test/process.test.ts`
Expected: FAIL because `segfault-handler` is imported unconditionally at module load time.

- [ ] **Step 3: Implement the minimal runtime fallback**

```typescript
function maybeRegisterSegfaultHandler() {
  try {
    const mod = require("segfault-handler");
    const handler = mod.default ?? mod;
    handler.registerHandler?.();
  } catch (error) {
    log.warn("segfault-handler unavailable; continuing without native crash handler", {
      error,
    });
  }
}
```

- [ ] **Step 4: Re-run the TypeScript test to verify it passes**

Run: `./b test -p src/server/shared/test/process.test.ts`
Expected: PASS.

### Task 3: Document the supported local boot path and validate it

**Files:**
- Modify: `README.md`
- Modify: `docs/docs/basics/running-locally.md`

- [ ] **Step 1: Update the docs with the repo-supported local path**

```markdown
- Preferred local path for this repo:
  1. Start `redis-server`
  2. Run `./b run --redis local`
  3. Visit `http://localhost:3000`

`--redis` selects the empty-bootstrap local flow and avoids depending on the snapshot bootstrap path for local bring-up.
```

- [ ] **Step 2: Update Python setup commands for macOS-friendly invocation**

```markdown
python3 -m venv .venv
python3 -m pip install -r requirements.txt
```

- [ ] **Step 3: Run focused validation commands**

Run: `python3 -m unittest discover -s scripts/b/test -p 'test_*.py'`
Expected: PASS.

Run: `./b test -p src/server/shared/test/process.test.ts`
Expected: PASS.

Run: `./b typecheck --pretty false src/server/shared/process.ts`
Expected: PASS.

Run: `python3 ./b run --help`
Expected: command help shows the updated alias choices, including `local`.

- [ ] **Step 4: Commit the completed work**

```bash
git add README.md docs/docs/basics/running-locally.md docs/superpowers/plans/2026-04-07-biomes-local-boot.md scripts/b/b.py scripts/b/pip_install_voxeloo.py scripts/b/test/test_local_boot.py src/server/shared/process.ts src/server/shared/test/process.test.ts
git commit -m "fix: make local biomes boot path reproducible"
```
