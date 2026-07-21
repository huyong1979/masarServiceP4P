# MASAR Service (EPICS 7 + Python 3)

This repository contains the NSLS-II MASAR server/client stack with:

- EPICS 7 C++ service (`cpp/`)
- Python client and server-side modules (`python/`)
- Pixi-managed runtime (`pixi.toml`, `pixi.lock`)

The project was flattened to this top-level layout (no nested `masarService/` subtree).

## Repository Layout

- `cpp/` - EPICS build tree for `masarServiceRun` and C++/Python bridge libs
- `python/` - MASAR Python packages and Qt UI code
- `start_server.cmd` - launch MASAR RPC server on channel `test`
- `start_client.cmd` - launch MASAR Qt client (default channel `test`)
- `test/` - legacy tests and examples
- `documentation/`, `example/` - docs and historical example content

## Requirements

- Linux x86_64
- EPICS Base installed at `/usr/lib/epics`
- Pixi environment (from `pixi.toml`) with Python 3.14 + PySide6

## Setup

From repository root:

```bash
pixi install
```

This creates `.pixi/envs/default` used by both launchers and the C++ build.

## Build (C++)

From repository root:

```bash
cd cpp
make -j4 -s
```

Notes:

- Build config is in `cpp/configure/RELEASE.local`.
- `PYTHON_BASE` must point to this repo's Pixi env:
  `/epics/op/apps/masarService/.pixi/envs/default`.

## Run

Start server:

```bash
./start_server.cmd
```

Start client (new terminal):

```bash
./start_client.cmd
```

Optional channel override:

```bash
./start_client.cmd <channel>
```

## Qt UI Regeneration

UI source files live in `python/masarclient/ui/*.ui`.

Regenerate generated Qt Python files and resources with:

```bash
./python/masarclient/ui/regen_ui.sh
```

This regenerates:

- `ui_commentdiag.py`
- `ui_commentdetail.py`
- `ui_masar.py`
- `masarRC_rc.py`

using Pixi `pyside6-uic`/`pyside6-rcc` through the environment's Python.

## Troubleshooting

- `Python.h: No such file or directory`
  - Verify `cpp/configure/RELEASE.local` `PYTHON_BASE` points to this repo's Pixi env.
- Embedded Python error (`No module named 'encodings'`) on server start
  - Ensure server is started via `./start_server.cmd` (it sets `PYTHONHOME`).
- Qt display/plugin errors on headless nodes
  - Use an X-capable session, or for smoke tests only:
    `QT_QPA_PLATFORM=offscreen ./start_client.cmd`.

## Current Defaults

- Server channel: `test`
- Client default channel: `test`
- SQLite DB path: `./masar.db`
