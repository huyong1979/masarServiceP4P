#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIXI_ENV="${ROOT_DIR}/.pixi/envs/default"

if [[ ! -x "${PIXI_ENV}/bin/python" ]]; then
    echo "Pixi Python not found at ${PIXI_ENV}/bin/python" >&2
    echo "Run 'pixi install' in ${ROOT_DIR} first." >&2
    exit 1
fi

export PYTHONPATH="${ROOT_DIR}/python:${ROOT_DIR}/cpp/src/python:${PYTHONPATH:-}"
export LD_LIBRARY_PATH="${PIXI_ENV}/lib:${ROOT_DIR}/cpp/lib/linux-x86_64:${LD_LIBRARY_PATH:-}"
export QT_API="pyside6"

channel="test"
if [[ $# -gt 0 ]]; then
    channel="$1"
fi

exec "${PIXI_ENV}/bin/python" - "${channel}" <<'PYCODE'
import sys

try:
    import masarclient.ui.masar as masar
except ModuleNotFoundError as exc:
    missing = exc.name or "unknown"
    if missing.startswith("matplotlib"):
        raise SystemExit(
            "Missing Python dependency: matplotlib.\n"
            "Install with: pixi add matplotlib"
        )
    raise

masar.main(channelname=sys.argv[1])
PYCODE
