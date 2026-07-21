#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIXI_ENV="${ROOT_DIR}/.pixi/envs/default"

export MASAR_SQLITE_DB="${ROOT_DIR}/masar.db"
export PYTHONHOME="${PIXI_ENV}"
export PYTHONPATH="${ROOT_DIR}/python:${ROOT_DIR}/cpp/src/python:${PYTHONPATH:-}"
export LD_LIBRARY_PATH="${PIXI_ENV}/lib:${ROOT_DIR}/cpp/lib/linux-x86_64:${LD_LIBRARY_PATH:-}"

exec "${ROOT_DIR}/cpp/bin/linux-x86_64/masarServiceRun" test
