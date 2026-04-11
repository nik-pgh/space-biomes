import os
import shutil
import subprocess
import sys
from functools import update_wrapper
from pathlib import Path

import b
import click


SCRIPT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
REPO_DIR = SCRIPT_DIR / ".." / ".."


def _resolve_python():
    """Return a Python binary path that actually exists.

    Resolution order:
      1. BIOMES_PYTHON env var (explicit user override)
      2. sys.executable   (the interpreter running this script)
      3. ``python3`` / ``python`` on PATH (last resort)

    Raises RuntimeError if nothing is found.
    """
    env_python = os.environ.get("BIOMES_PYTHON")
    if env_python:
        if shutil.which(env_python) or os.path.isfile(env_python):
            return env_python
        raise RuntimeError(
            f"BIOMES_PYTHON is set to '{env_python}' but that executable was not found."
        )

    if sys.executable:
        return sys.executable

    for name in ("python3", "python"):
        found = shutil.which(name)
        if found:
            return found

    raise RuntimeError(
        "No Python interpreter found. Install Python 3.9+ or set the "
        "BIOMES_PYTHON environment variable to the path of your interpreter."
    )


def ensure_pip_install_voxeloo(f):
    """
    Wrapper to make sure voxeloo is built and up-to-date before proceeding.
    """

    @click.pass_context
    def with_check(ctx, *args, **kwargs):
        # Most things that want an up-to-date voxeloo also want up-to-date ts.
        b.ensure_bazel_up_to_date(ctx)
        if "VOXELOO_BUILT" not in ctx.obj:
            run_pip_install_voxeloo()
            ctx.obj["VOXELOO_BUILT"] = True
        return ctx.invoke(f, *args, **kwargs)

    return update_wrapper(with_check, f)


def run_pip_install_voxeloo():
    python = _resolve_python()
    click.secho(f"Running `{python} -m pip install ./voxeloo`...")
    click.secho()
    result = subprocess.run(
        [python, "-m", "pip", "install", "./voxeloo"], cwd=REPO_DIR
    )
    if result.returncode != 0:
        sys.exit(result.returncode)


def run_pip_install_requirements():
    python = _resolve_python()
    click.secho(f"Running `{python} -m pip install -r requirements.txt`...")
    click.secho()
    result = subprocess.run(
        [python, "-m", "pip", "install", "-r", "requirements.txt"], cwd=REPO_DIR
    )
    if result.returncode != 0:
        sys.exit(result.returncode)
