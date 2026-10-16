#!/usr/bin/env bash
#
# Launch the pure-Python MASAR RPC server (p4p / PVXS / QSRV2).
# Drop-in replacement for start_server.cmd (which runs the legacy C++
# masarServiceRun).  No C++ libraries are required.
#
# Usage:  ./start_server_p4p.cmd [channelName]
#         default channel name: testp4p
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIXI_ENV="${ROOT_DIR}/.pixi/envs/default"
if [[ ! -x "${PIXI_ENV}/bin/python" ]]; then
    echo "Pixi Python not found at ${PIXI_ENV}/bin/python" >&2
    echo "Run 'pixi install' in ${ROOT_DIR} first." >&2
    exit 1
fi

CHANNEL="${1:-masar_p4p}"

# pvAccess server port in case the default 5075 is already used.
export EPICS_PVA_SERVER_PORT=5078

# Database and Python backend.
export MASAR_SQLITE_DB="${ROOT_DIR}/masar.db"
export PYTHONPATH="${ROOT_DIR}/python:${PYTHONPATH:-}"

# Channel Access library (libca) for live-machine gather via cothread.catools.
# cothread.load_ca locates libca from $EPICS_BASE/lib/$EPICS_HOST_ARCH.  The
# pixi environment ships a self-contained EPICS build, so point at it and put
# its lib dir on LD_LIBRARY_PATH so libca's dependency (libCom) also resolves.
export EPICS_BASE="${EPICS_BASE:-${PIXI_ENV}/epics}"
export EPICS_HOST_ARCH="${EPICS_HOST_ARCH:-linux-x86_64}"
export LD_LIBRARY_PATH="${EPICS_BASE}/lib/${EPICS_HOST_ARCH}:${PIXI_ENV}/lib:${LD_LIBRARY_PATH:-}"


exec "${PIXI_ENV}/bin/python" \
     "${ROOT_DIR}/python/masarserver/masarServer_p4p.py" "${CHANNEL}"
