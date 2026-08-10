import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from functools import update_wrapper
from pathlib import Path

import b
import click
from pip_install_voxeloo import (run_pip_install_requirements,
                                 run_pip_install_voxeloo)

SCRIPT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
REPO_DIR = SCRIPT_DIR / ".." / ".."

ERROR_COLOR = "bright_red"
WARNING_COLOR = "bright_yellow"
GOOD_COLOR = "bright_green"

ASSET_VERSIONS_PATH = REPO_DIR / "src" / "galois" / "js" / "interface" / "gen" / "asset_versions.json"
SNAPSHOT_BUCKETS_DIR_NAME = "buckets"
SNAPSHOT_BUCKETS_PATH = REPO_DIR / "public" / SNAPSHOT_BUCKETS_DIR_NAME
SNAPSHOT_BUCKETS_URL_PREFIX = f"/{SNAPSHOT_BUCKETS_DIR_NAME}/"
STATIC_BUCKET_PATH = SNAPSHOT_BUCKETS_PATH / "biomes-static"
BIKKIE_BUCKET_PATH = SNAPSHOT_BUCKETS_PATH / "biomes-bikkie"
BIKKIE_STATIC_PREFIX = f"{SNAPSHOT_BUCKETS_URL_PREFIX}biomes-bikkie/"
GALOIS_STATIC_PREFIX = f"{SNAPSHOT_BUCKETS_URL_PREFIX}biomes-static/"

GS_URL_BASE = "gs://biomes-static"
DEFAULT_DOWNLOAD_URL_BASE = "https://static.biomes.gg"

DATA_SNAPSHOT_FILENAME = "biomes_data_snapshot.tar.gz"
DATA_SNAPSHOT_GS_URL = f"{GS_URL_BASE}/{DATA_SNAPSHOT_FILENAME}"


def _snapshot_download_url():
    """Return the snapshot download URL, overridable via BIOMES_SNAPSHOT_URL."""
    base = os.environ.get("BIOMES_SNAPSHOT_URL")
    if base:
        return base
    return f"{DEFAULT_DOWNLOAD_URL_BASE}/{DATA_SNAPSHOT_FILENAME}"


def _snapshot_local_file():
    """Return a local snapshot file path if BIOMES_SNAPSHOT_FILE is set."""
    path = os.environ.get("BIOMES_SNAPSHOT_FILE")
    if path and not os.path.isfile(path):
        raise RuntimeError(
            f"BIOMES_SNAPSHOT_FILE is set to '{path}' but that file does not exist."
        )
    return path


def _snapshot_local_dir():
    """Return a local snapshot directory if BIOMES_SNAPSHOT_DIR is set."""
    path = os.environ.get("BIOMES_SNAPSHOT_DIR")
    if path and not os.path.isdir(path):
        raise RuntimeError(
            f"BIOMES_SNAPSHOT_DIR is set to '{path}' but that directory does not exist."
        )
    return path


def _print_minimal_boot_warning():
    click.secho(
        "Continuing with minimal local boot validation despite missing assets.",
        fg=WARNING_COLOR,
    )
    click.secho(
        "Tradeoff: missing biomes-static assets can still 404 at runtime; this path validates bring-up, not full local asset completeness.",
        fg=WARNING_COLOR,
    )
    click.secho(
        "Recommended seed: BIOMES_SNAPSHOT_DIR=$PWD/tmp/reconstructed-snapshot",
        fg=WARNING_COLOR,
    )

SNAPSHOT_BACKUP_PATH = REPO_DIR / "snapshot_backup.json"

REDIS_BOOTSTRAP_HASH_KEY = "biomes_data_snapshot_hash"


@click.group()
def data_snapshot():
    """Commands for working with data snapshots."""
    pass


@data_snapshot.command()
@click.argument(
    "path",
    type=str,
)
@click.pass_context
def create_to_file(ctx, path: str):
    """Creates a data snapshot by pulling from prod. Needs gcloud auth."""

    if not path.endswith(".tar.gz"):
        raise RuntimeError(f"Path '{path}' does not end with '.tar.gz'.")

    # Ensure path doesn't already exist.
    if os.path.exists(path):
        raise RuntimeError(f"Path '{path}' already exists.")

    # Create a temporary directory to collect snapshot files in.
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_file = Path(tmpdir) / "backup.json"
        buckets_dir = Path(tmpdir) / "buckets"

        # Pull the latest backup file.
        click.secho("Downloading the latest backup file...")
        ctx.invoke(b.fetch, destination=backup_file)

        # Download the bucket asset data.
        click.secho("Downloading static assets...")
        ctx.invoke(b.script, name="extract_assets", args=[buckets_dir])

        # Tar up the directory.
        click.secho("Creating tarball...")
        subprocess.run(["tar", "-czf", path, "-C", tmpdir, "."])

    click.secho(f"Created data snapshot at '{path}'.")


@data_snapshot.command()
@click.argument(
    "path",
    type=str,
)
def upload_from_file(path: str):
    """Uploads specified file to GCS as the new current data snapshot. Needs gcloud auth."""

    # Check that path exists.
    if not os.path.exists(path):
        raise RuntimeError(f"Path '{path}' does not exist.")

    click.secho(
        f"Uploading data snapshot from file '{path}' to '{DATA_SNAPSHOT_GS_URL}'..."
    )
    subprocess.run(["gsutil", "cp", path, DATA_SNAPSHOT_GS_URL])

    click.secho("Done uploading data snapshot.")


def hash_file(path: str):
    """Returns the MD5 hash of the file at path."""
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


@data_snapshot.command()
@click.pass_context
def push(ctx):
    """Creates new data snapshot and uploads it to GCS as new current. Needs gcloud auth."""

    # Create temporary directory work within.
    with tempfile.TemporaryDirectory() as tmpdir:
        path = str(Path(tmpdir) / DATA_SNAPSHOT_FILENAME)

        ctx.invoke(create_to_file, path=path)
        ctx.invoke(upload_from_file, path=path)


def _install_snapshot_from_unpacked_dir(path: Path):
    backup_path = path / "backup.json"
    buckets_path = path / "buckets"

    if not backup_path.is_file():
        raise RuntimeError(
            f"Snapshot directory '{path}' is missing required file 'backup.json'."
        )
    if not buckets_path.is_dir():
        raise RuntimeError(
            f"Snapshot directory '{path}' is missing required directory 'buckets'."
        )

    if SNAPSHOT_BACKUP_PATH.exists():
        SNAPSHOT_BACKUP_PATH.unlink()
    shutil.copy2(backup_path, SNAPSHOT_BACKUP_PATH)

    SNAPSHOT_BUCKETS_PATH.mkdir(exist_ok=True, parents=True)
    for file in buckets_path.iterdir():
        dir = SNAPSHOT_BUCKETS_PATH / file.name
        if dir.exists():
            shutil.rmtree(dir)
        shutil.copytree(file, dir)


@data_snapshot.command()
@click.argument(
    "path",
    type=str,
)
def install_from_file(path: str):
    """Install a data snapshot from a file."""
    click.secho(f"Installing data snapshot from file '{path}'...")

    # Ensure the file exists.
    if not os.path.exists(path):
        raise RuntimeError(f"File '{path}' does not exist.")

    # Create a temporary directory to unpack into.
    with tempfile.TemporaryDirectory() as tmpdir:
        # Unpack the file.
        subprocess.run(["tar", "-xzf", path, "-C", tmpdir], check=True)
        _install_snapshot_from_unpacked_dir(Path(tmpdir))

    click.secho(f"Done installing data snapshot.")


@data_snapshot.command()
@click.argument(
    "path",
    type=str,
)
def install_from_directory(path: str):
    """Install a data snapshot from an already unpacked directory."""
    click.secho(f"Installing data snapshot from directory '{path}'...")

    source_path = Path(path)
    if not source_path.is_dir():
        raise RuntimeError(f"Directory '{path}' does not exist.")

    _install_snapshot_from_unpacked_dir(source_path)
    click.secho("Done installing data snapshot.")


@data_snapshot.command()
def uninstall():
    """Removes all installed data snapshot files from your repository."""
    # Remove SNAPSHOT_BACKUP_PATH.
    if SNAPSHOT_BACKUP_PATH.exists():
        SNAPSHOT_BACKUP_PATH.unlink()

    # Remove the specific buckets directory.
    if STATIC_BUCKET_PATH.exists():
        shutil.rmtree(STATIC_BUCKET_PATH)

    if BIKKIE_BUCKET_PATH.exists():
        shutil.rmtree(BIKKIE_BUCKET_PATH)


def is_installed():
    return (
        SNAPSHOT_BACKUP_PATH.exists()
        and STATIC_BUCKET_PATH.exists()
        and BIKKIE_BUCKET_PATH.exists()
    )


@data_snapshot.command()
@click.argument(
    "path",
    type=str,
)
def download_to_file(path: str):
    """Download the latest data snapshot to a file.

    The download URL defaults to the upstream static.biomes.gg host but can be
    overridden with the BIOMES_SNAPSHOT_URL environment variable.
    """
    url = _snapshot_download_url()
    click.secho(
        f"Downloading latest data snapshot from '{url}' to '{path}'..."
    )

    # Ensure the output file does not already exist.
    if os.path.exists(path):
        raise RuntimeError(f"File '{path}' already exists.")

    # Download the file. Use curl to get a progress bar.
    # --fail makes curl return exit code 22 on HTTP errors (4xx/5xx).
    result = subprocess.run(["curl", "--fail", "-L", url, "--output", path])
    if result.returncode != 0:
        # Clean up partial download so later steps don't see a corrupt file.
        if os.path.exists(path):
            os.remove(path)
        raise RuntimeError(
            f"Snapshot download failed (curl exit code {result.returncode}).\n"
            f"  URL: {url}\n"
            f"  Hint: If the upstream host is unavailable, download the snapshot\n"
            f"  manually and point to it with:\n"
            f"    export BIOMES_SNAPSHOT_FILE=/path/to/biomes_data_snapshot.tar.gz\n"
            f"  Or provide an alternate URL:\n"
            f"    export BIOMES_SNAPSHOT_URL=https://your-mirror/biomes_data_snapshot.tar.gz"
        )

    click.secho(f"Data snapshot downloaded to {path}.")


@data_snapshot.command()
@click.pass_context
def pull(ctx):
    """If out of date, downloads and installs the latest snapshot data.

    Set BIOMES_SNAPSHOT_DIR to an unpacked local snapshot directory.
    Set BIOMES_SNAPSHOT_FILE to a local .tar.gz path to skip the download.
    Set BIOMES_SNAPSHOT_URL to use an alternate download URL.
    """

    if is_installed():
        click.secho(f"Snapshot is already installed, nothing to do.")
        return

    # Allow supplying an already reconstructed snapshot directory.
    local_dir = _snapshot_local_dir()
    if local_dir:
        click.secho(f"Using local snapshot directory: {local_dir}")
        ctx.invoke(install_from_directory, path=local_dir)
        click.secho("Installed snapshot data from local directory.")
        return

    # Allow supplying a pre-downloaded snapshot file.
    local_file = _snapshot_local_file()
    if local_file:
        click.secho(f"Using local snapshot file: {local_file}")
        ctx.invoke(install_from_file, path=local_file)
        click.secho(f"Installed snapshot data from local file.")
        return

    # Download to a temp directory, then install.
    with tempfile.TemporaryDirectory() as tmpdir:
        path = str(Path(tmpdir) / DATA_SNAPSHOT_FILENAME)

        # Download the snapshot.
        ctx.invoke(download_to_file, path=path)

        # Install the snapshot.
        ctx.invoke(install_from_file, path=path)

    click.secho(f"Installed snapshot data is up-to-date.")


@data_snapshot.command()
@click.pass_context
def populate_redis(ctx):
    """Populate a running redis-server with the installed snapshot data."""
    if not redis_server_started():
        raise RuntimeError("Expected redis-server to be started already.")

    # If we've previously bootstrapped, check with the user before proceeding
    # to clear and overwrite.
    if redis_cli(f"exists {REDIS_BOOTSTRAP_HASH_KEY}").strip() == "1":
        click.secho(
            "Your Redis DB has been bootstrapped with older data, proceeding will reset it with new data."
        )

    # Clear out the local redis database before proceeding to bootstrap it.
    if not click.confirm("Clearing data on your local redis-server. Proceed?"):
        return
    redis_cli("flushall")

    click.secho(
        f"Populating redis with data from backup file '{SNAPSHOT_BACKUP_PATH}'...."
    )
    ctx.invoke(b.script, name="bootstrap_redis", args=[SNAPSHOT_BACKUP_PATH])

    # Remember the hash of the backup that we bootstrapped redis with.
    hash = hash_file(SNAPSHOT_BACKUP_PATH)
    redis_cli(f"set {REDIS_BOOTSTRAP_HASH_KEY} {hash}")
    redis_cli("save")

    click.secho("Done populating redis.")


@data_snapshot.command()
@click.pass_context
def ensure_redis_populated(ctx):
    """Populate a running redis-server with the installed snapshot data."""
    if not redis_server_started():
        raise RuntimeError("Expected redis-server to be started already.")

    # Ensure that SNAPSHOT_HASH_PATH exists, since it marks if installation
    # has been performed.
    if not is_installed():
        raise RuntimeError("No data snapshot has been installed.")

    # Compare the current hash of the data snapshot that we bootstrapped redis with to the hash of the installed snapshot data.
    installed_hash = hash_file(SNAPSHOT_BACKUP_PATH)
    bootstrapped_hash = redis_cli(f"get {REDIS_BOOTSTRAP_HASH_KEY}")
    if installed_hash.strip() == bootstrapped_hash.strip():
        click.secho(
            "Redis is already populated with the installed snapshot data."
        )
        return

    ctx.invoke(populate_redis)


def _run_with_snapshot(ctx, pip_install: bool, error_on_missing_assets: bool):
    if pip_install:
        run_pip_install_requirements()
        run_pip_install_voxeloo()

    subprocess.run(["git", "lfs", "pull"], cwd=REPO_DIR, check=True)

    # Make sure our data snapshot exists and is up-to-date.
    ctx.invoke(pull)
    assets_missing = ctx.invoke(
        check_for_missing_assets, error_on_missing=error_on_missing_assets
    )
    if assets_missing and not error_on_missing_assets:
        _print_minimal_boot_warning()

    with RedisServer():
        # Make sure our Redis server is populated with the data snapshot.
        ctx.invoke(ensure_redis_populated)

        # Actually run a local Biomes server.
        ctx.invoke(
            b.run,
            target=["web"],
            redis=True,
            storage="memory",
            assets="local",
            open_admin_access=True,
            bikkie_static_prefix=BIKKIE_STATIC_PREFIX,
            galois_static_prefix=GALOIS_STATIC_PREFIX,
            local_gcs=True,
        )


@data_snapshot.command()
@click.option(
    "--pip-install/--no-pip-install",
    help="Whether or not `pip install ./voxeloo` will get called before commands that need it.",
    default=True,
)
@click.pass_context
def run(ctx, pip_install: bool):
    """Run with from data snapshot."""
    _run_with_snapshot(
        ctx, pip_install=pip_install, error_on_missing_assets=True
    )


@data_snapshot.command()
@click.option(
    "--pip-install/--no-pip-install",
    help="Whether or not `pip install ./voxeloo` will get called before commands that need it.",
    default=True,
)
@click.pass_context
def run_minimal(ctx, pip_install: bool):
    """Run a minimal local boot validation path without requiring full asset completeness."""
    _run_with_snapshot(
        ctx, pip_install=pip_install, error_on_missing_assets=False
    )


def redis_cli(command: str, db=0):
    args = ["redis-cli", "-n", str(db)]
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    return p.communicate(command.encode(), timeout=60)[0].decode()


def redis_server_started():
    ping = subprocess.Popen(["redis-cli", "ping"], stdout=subprocess.PIPE)
    return ping.communicate()[0] == b"PONG\n"


MAX_REDIS_STARTUP_TIME = 120
class RedisServer(object):
    def __init__(self):
        pass

    def __enter__(self):
        click.secho("Starting redis-server...", fg=WARNING_COLOR)
        self.process = subprocess.Popen("redis-server")
        # Wait for server to start.
        start_time = time.time()
        last_message_time = start_time
        while True:
            if redis_server_started():
                break
            time.sleep(1)
            now = time.time()
            if now - last_message_time > 5:
                last_message_time = now
                click.secho("Starting redis-server...", fg=WARNING_COLOR)
            if now - start_time > MAX_REDIS_STARTUP_TIME:
                self.process.terminate()
                raise RuntimeError("redis-server failed to start.")
        click.secho("redis-server started", fg=GOOD_COLOR)

        return self.process

    def __exit__(self, *args):
        click.secho("Killing redis-server...")
        self.process.kill()
        try:
            self.process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            click.secho(
                "redis-server timed out while shutting down, terminating."
            )
            self.process.terminate()

        click.secho("redis-server shutdown.")

def fetch_asset_versions():
    with open(ASSET_VERSIONS_PATH, 'r') as file:
        asset_versions = json.load(file)["paths"]

    return [(name, asset_versions[name]) for name in asset_versions]

# Verify that the assets referenced in asset_versions.json have been downloaded.
# Returns True if there are missing assets.
@data_snapshot.command()
@click.option(
    "--error-on-missing/--no-error-on-missing",
    help="Whether or not to throw an error when an asset is missing.",
    default=True,
)
@click.pass_context
def check_for_missing_assets(ctx, error_on_missing=True) -> bool:
    asset_versions = fetch_asset_versions()
    assets_missing = False;
    for (name, asset_path) in asset_versions:
        relative_asset_path = f"{STATIC_BUCKET_PATH}/{asset_path}"
        if not os.path.isfile(relative_asset_path):
            click.secho(f"Asset not found: {name}", fg=WARNING_COLOR)
            assets_missing = True

    if assets_missing and error_on_missing:
        raise Exception("Missing assets\nConsider running:\n$ git pull\n$ ./b data-snapshot uninstall\n$ ./b data-snapshot install\nto fetch the most up-to-date assets.")
    elif not assets_missing:
        click.secho("Assets are up-to-date", fg=GOOD_COLOR)
    return assets_missing

