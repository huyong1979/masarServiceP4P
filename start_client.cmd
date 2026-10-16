#!/usr/bin/env bash
set -euo pipefail
# Example: ./start_client.cmd diagioc-spc testp4p

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIXI_ENV="${ROOT_DIR}/.pixi/envs/default"
if [[ ! -x "${PIXI_ENV}/bin/python" ]]; then
    echo "Pixi Python not found at ${PIXI_ENV}/bin/python" >&2
    echo "Run 'pixi install' in ${ROOT_DIR} first." >&2
    exit 1
fi

# Pure-Python client (p4p/PVXS): the compiled masar C++ modules under
# cpp/src/python are no longer needed, so they are left off PYTHONPATH.
export PYTHONPATH="/epics/op/apps/pyOlog:${ROOT_DIR}/python:${PYTHONPATH:-}"
export LD_LIBRARY_PATH="${PIXI_ENV}/lib:${LD_LIBRARY_PATH:-}"

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

# MASAR server: pvAccess server port
export EPICS_PVA_SERVER_PORT=5078

# MASAR server: default to the client host itself
# Optional: pass remote server host/IP as 2nd arg.

server_addr="${MASAR_SERVER_ADDR:-}"
if [[ $# -gt 0 ]]; then
    server_addr="$1"
fi
if [[ -z "${server_addr}" ]]; then
    server_addr="$(hostname -s 2>/dev/null || true)"
fi
if [[ -n "${server_addr}" ]]; then
    # Pure-Python client uses p4p/PVXS, which DOES support TCP name-server
    # discovery (EPICS_PVA_NAME_SERVERS).  Point it straight at the server's
    # TCP port (EPICS_PVA_SERVER_PORT).  This is the most robust option for a
    # cross-subnet server because it avoids UDP search entirely and therefore
    # the stateful-firewall "search reply dropped" problem that affected the
    # old libpvAccess client.  Unicast UDP search is kept as a fallback.
    #   Also avoids a foreign pvAccess server on the local subnet that exports
    #   an unrelated channel of the same name (broadcast would find it first).
    export EPICS_PVA_NAME_SERVERS="${server_addr}:${EPICS_PVA_SERVER_PORT}"
    export EPICS_PVA_ADDR_LIST="${server_addr}"
    export EPICS_PVA_AUTO_ADDR_LIST="NO"
fi

channel="masar_p4p"
if [[ $# -gt 1 ]]; then
    channel="$2"
fi

echo "Connecting to ${server_addr}:${EPICS_PVA_SERVER_PORT} on channel ${channel}"

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
