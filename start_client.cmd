#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIXI_ENV="${ROOT_DIR}/.pixi/envs/default"

if [[ ! -x "${PIXI_ENV}/bin/python" ]]; then
    echo "Pixi Python not found at ${PIXI_ENV}/bin/python" >&2
    echo "Run 'pixi install' in ${ROOT_DIR} first." >&2
    exit 1
fi

export PYTHONPATH="/epics/op/apps/pyOlog:${ROOT_DIR}/python:${ROOT_DIR}/cpp/src/python:${PYTHONPATH:-}"
export LD_LIBRARY_PATH="${PIXI_ENV}/lib:${ROOT_DIR}/cpp/lib/linux-x86_64:${LD_LIBRARY_PATH:-}"
export QT_API="pyside6"

if [[ -f "/etc/fonts/fonts.conf" ]]; then
    export FONTCONFIG_FILE="/etc/fonts/fonts.conf"
fi
if [[ -d "/etc/fonts" ]]; then
    export FONTCONFIG_PATH="/etc/fonts"
fi
if [[ -f "/usr/share/X11/locale/en_US.UTF-8/Compose" ]]; then
    export XCOMPOSEFILE="/usr/share/X11/locale/en_US.UTF-8/Compose"
fi

channel="test"
if [[ $# -gt 0 ]]; then
    channel="$1"
fi

# Optional: pass remote server host/IP as 2nd arg.
# Example: ./start_client.cmd test diagioc-spc.nsls2.bnl.local
server_addr="${MASAR_SERVER_ADDR:-}"
if [[ $# -gt 1 ]]; then
    server_addr="$2"
fi
if [[ -z "${server_addr}" ]]; then
    host_short="$(hostname -s 2>/dev/null || true)"
    if [[ "${host_short}" != "diagioc-spc" ]]; then
        server_addr="diagioc-spc.nsls2.bnl.local"
    fi
fi
if [[ -n "${server_addr}" ]]; then
    export EPICS_PVA_ADDR_LIST="${server_addr}"
    export EPICS_PVA_AUTO_ADDR_LIST="NO"
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
