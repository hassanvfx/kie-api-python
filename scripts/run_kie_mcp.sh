#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"
venv_python="${repo_root}/.venv/bin/python"
venv_mcp="${repo_root}/.venv/bin/kie-mcp"
env_file="${repo_root}/.env"

cd "${repo_root}"

if [[ ! -x "${venv_python}" ]]; then
  cat >&2 <<EOF
Missing virtualenv at ${repo_root}/.venv

Run:
  python3 -m venv .venv
  .venv/bin/python -m pip install -e ".[dev,mcp]"
EOF
  exit 1
fi

if [[ ! -x "${venv_mcp}" ]]; then
  cat >&2 <<EOF
Missing kie-mcp entrypoint at ${venv_mcp}

Run:
  .venv/bin/python -m pip install -e ".[dev,mcp]"
EOF
  exit 1
fi

if [[ -z "${KIE_API_KEY:-}" && ! -f "${env_file}" ]]; then
  cat >&2 <<EOF
Warning: KIE_API_KEY is not set and ${env_file} does not exist.
The MCP server can still start, but live KIE calls will fail until credentials are available.
EOF
fi

exec "${venv_mcp}" "$@"
