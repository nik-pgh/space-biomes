#!/usr/bin/env bash
set -euo pipefail

if [[ $# -eq 0 ]]; then
  echo "usage: $0 <command> [args...]" >&2
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${BIOMES_PYTHON_VENV:-${REPO_ROOT}/.biomes/python3.10}"
VENV_PYTHON="${VENV_DIR}/bin/python"

canonical_path() {
  local target="$1"
  if [[ -z "${target}" ]]; then
    return 1
  fi

  python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "${target}"
}

find_python310() {
  if [[ -n "${BIOMES_PYTHON:-}" && -x "${BIOMES_PYTHON}" && "$(canonical_path "${BIOMES_PYTHON}" || true)" != "$(canonical_path "${VENV_PYTHON}" || true)" ]]; then
    echo "${BIOMES_PYTHON}"
    return 0
  fi

  local candidates=(
    "/opt/homebrew/bin/python3.10"
    "/usr/local/bin/python3.10"
    "${HOME}/.pyenv/shims/python3.10"
  )

  local candidate
  for candidate in "${candidates[@]}"; do
    if [[ -x "${candidate}" ]]; then
      echo "${candidate}"
      return 0
    fi
  done

  if command -v python3.10 >/dev/null 2>&1; then
    command -v python3.10
    return 0
  fi

  return 1
}

ensure_venv() {
  local source_python="$(find_python310 || true)"
  if [[ -z "${source_python}" ]]; then
    cat >&2 <<'EOF'
error: could not find a supported Python 3.10 interpreter for Biomes.

Expected one of:
  /opt/homebrew/bin/python3.10
  /usr/local/bin/python3.10
  python3.10 on PATH

Install one, for example on macOS:
  brew install python@3.10

Or set BIOMES_PYTHON to an explicit python3.10 executable and retry.
EOF
    exit 1
  fi

  local expected_python="$(canonical_path "${source_python}")"

  if [[ ! -x "${VENV_PYTHON}" ]]; then
    mkdir -p "$(dirname "${VENV_DIR}")"
    "${source_python}" -m venv "${VENV_DIR}"
  fi

  local actual_python=""
  if [[ -x "${VENV_PYTHON}" ]]; then
    actual_python="$(canonical_path "${VENV_PYTHON}")"
  fi

  if [[ -n "${actual_python}" && "${actual_python}" != "${expected_python}" ]]; then
    rm -rf "${VENV_DIR}"
    mkdir -p "$(dirname "${VENV_DIR}")"
    "${source_python}" -m venv "${VENV_DIR}"
  fi
}

ensure_venv

export BIOMES_PYTHON="${VENV_PYTHON}"
export PATH="${VENV_DIR}/bin:${PATH}"
exec "$@"
