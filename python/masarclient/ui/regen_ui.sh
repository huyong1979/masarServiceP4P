#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
PIXI_ENV="${ROOT_DIR}/.pixi/envs/default"
UIC="${PIXI_ENV}/bin/pyside6-uic"
RCC="${PIXI_ENV}/bin/pyside6-rcc"
PYTHON="${PIXI_ENV}/bin/python"
UI_DIR="${SCRIPT_DIR}"

if [[ ! -x "${PYTHON}" ]]; then
    echo "Missing Pixi Python at ${PYTHON}" >&2
    echo "Run 'pixi install' in ${ROOT_DIR} first." >&2
    exit 1
fi

if [[ ! -x "${UIC}" ]]; then
    echo "Missing pyside6-uic at ${UIC}" >&2
    echo "Run 'pixi install' in ${ROOT_DIR} first." >&2
    exit 1
fi

if [[ ! -x "${RCC}" ]]; then
    echo "Missing pyside6-rcc at ${RCC}" >&2
    echo "Run 'pixi install' in ${ROOT_DIR} first." >&2
    exit 1
fi

"${PYTHON}" "${UIC}" --from-imports "${UI_DIR}/ui_commentdiag.ui" -o "${UI_DIR}/ui_commentdiag.py"
"${PYTHON}" "${UIC}" --from-imports "${UI_DIR}/ui_commentdetail.ui" -o "${UI_DIR}/ui_commentdetail.py"
"${PYTHON}" "${UIC}" --from-imports "${UI_DIR}/ui_masar.ui" -o "${UI_DIR}/ui_masar.py"
"${PYTHON}" "${RCC}" "${UI_DIR}/masarRC.qrc" -o "${UI_DIR}/masarRC_rc.py"

echo "Regenerated UI Python files and Qt resources in ${UI_DIR}"
