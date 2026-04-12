import importlib.util
import os
import shutil
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

sys.modules.setdefault("b", types.SimpleNamespace())
sys.modules.setdefault(
    "pip_install_voxeloo",
    types.SimpleNamespace(
        run_pip_install_requirements=lambda: None,
        run_pip_install_voxeloo=lambda: None,
    ),
)

spec = importlib.util.spec_from_file_location(
    "issue32_data_snapshot", REPO / "scripts" / "b" / "data_snapshot.py"
)
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)

snapshot_dir = Path(os.environ.get("BIOMES_SNAPSHOT_DIR", REPO / "tmp" / "reconstructed-snapshot"))
print(f"Using local snapshot directory: {snapshot_dir}")

if not snapshot_dir.is_dir():
    raise SystemExit(f"Missing snapshot dir: {snapshot_dir}")

for path in [REPO / "snapshot_backup.json", REPO / "public" / "buckets" / "biomes-static", REPO / "public" / "buckets" / "biomes-bikkie"]:
    if path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)

resolved_local_dir = ds._snapshot_local_dir()
print(f"data_snapshot._snapshot_local_dir(): {resolved_local_dir}")
if resolved_local_dir != str(snapshot_dir):
    raise SystemExit("BIOMES_SNAPSHOT_DIR did not resolve to the expected local path")

print("Installing from local directory without any download step...")
ds._install_snapshot_from_unpacked_dir(snapshot_dir)

print(f"snapshot_backup.json exists: {(REPO / 'snapshot_backup.json').is_file()}")
print(f"public/buckets/biomes-static exists: {(REPO / 'public' / 'buckets' / 'biomes-static').is_dir()}")
print(f"public/buckets/biomes-bikkie exists: {(REPO / 'public' / 'buckets' / 'biomes-bikkie').is_dir()}")
print("Validation completed.")
