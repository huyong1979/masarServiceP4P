# MASAR Service (EPICS 7 + Python, p4p/PVXS)

MASAR stands for **MAchine Snapshot, Archiving, and Retrieve**.

This repository contains the NSLS-II MASAR server/client stack as a
**pure-Python** implementation built on [p4p](https://mdavidsaver.github.io/p4p/)
(PVXS / QSRV2). The legacy EPICS 7 C++ service and its compiled Python bridge
modules have been removed — no C++ build is required anymore.

- **Server:** pure-Python pvAccess RPC service (`python/masarserver/masarServer_p4p.py`)
- **Client/GUI:** PySide6 Qt application (`python/masarclient/`)
- **Backend:** SQLite via the `pymasarsqlite` package
- **Live-machine access:** Channel Access gather/put via `cothread.catools`
- **Runtime:** Pixi-managed environment (`pixi.toml`, `pixi.lock`)

## Repository Layout

- `python/` — MASAR Python packages
  - `masarserver/` — `masarServer_p4p.py`, the p4p RPC server
  - `masarclient/` — p4p client (`masarClient.py`, `channelRPC.py`) and Qt UI (`ui/`)
  - `pymasarsqlite/` — SQLite backend (service/config/event/snapshot data access)
    - `db/` — schema (`masar-sqlite.sql`) and helper scripts to create a fresh database
- `start_server_p4p.cmd` — launch the MASAR RPC server
- `start_client.cmd` — launch the MASAR Qt client
- `masar_example.db` — reference SQLite database (tracked, for first-time setup)
- `masar.db` — local/production database (git-ignored; copy your own here)
- `pixi.toml` / `pixi.lock` — Pixi environment definition
- `wheels/` — bundled wheels (e.g. `cothread`)

## Requirements

- Linux x86_64
- Pixi (https://pixi.sh)
- The Pixi environment provides everything else: Python 3.14, PySide6, p4p,
  cothread, matplotlib, and a self-contained EPICS build (`libca`/`libCom`) used
  for live-machine Channel Access. No system EPICS installation is needed.

## Setup

From the repository root:

```bash
pixi install
```

This creates `.pixi/envs/default`, which both launchers use.

For a fresh deployment, provide a database. Either copy the bundled example:

```bash
cp masar_example.db masar.db
```

or copy your production `masar.db` into the repository root.

## Run

Start the server:

```bash
./start_server_p4p.cmd [channelName]
```

- Default channel: `masar_p4p`
- Serves pvAccess on TCP port `5078` (`EPICS_PVA_SERVER_PORT`)
- Uses `./masar.db` (`MASAR_SQLITE_DB`)
- Points `cothread` at the Pixi-bundled `libca` via `EPICS_BASE` /
  `EPICS_HOST_ARCH` so live-machine gather works

Start the client (new terminal):

```bash
./start_client.cmd [serverHost] [channelName]
```

- `serverHost` — MASAR server host (defaults to the local host; set
  `MASAR_SERVER_ADDR` to override). The client reaches the server via pvAccess
  TCP name-server discovery (`EPICS_PVA_NAME_SERVERS=<serverHost>:5078`), which
  is robust across subnets/firewalls.
- `channelName` — defaults to `masar_p4p` (must match the server's channel)

Example (remote server, custom channel):

```bash
./start_client.cmd diagioc-spc masar_p4p
```

### Channel Access for live-machine operations

Compare Live Machine, Restore Machine, and Save Machine Snapshot use Channel
Access:

- The **server** gathers live PV values via `cothread.catools`. Ensure the
  server host can reach the machine PVs (set `EPICS_CA_ADDR_LIST` /
  `EPICS_CA_NAME_SERVERS` in its environment if a gateway is required).
- The **client** reads a maintenance-guard PV and performs restore puts directly
  via CA, so the client host also needs CA reachability to those PVs.

## Qt UI Regeneration

Qt Designer sources live in `python/masarclient/ui/*.ui`. Regenerate the
generated Python and resource files with:

```bash
./python/masarclient/ui/regen_ui.sh
```

This regenerates `ui_masar.py`, `ui_commentdiag.py`, `ui_commentdetail.py`, and
`masarRC_rc.py` using the Pixi environment's `pyside6-uic` / `pyside6-rcc`.

## Troubleshooting

- **"Exception occurred when retrieving live data"** (Compare/Restore/Save)
  - The server's `cothread.catools` gather failed. Check the server terminal for
    a traceback. A `KeyError: 'EPICS_BASE'` means `libca` could not be located —
    `start_server_p4p.cmd` sets `EPICS_BASE`/`EPICS_HOST_ARCH` for this.
  - Otherwise verify Channel Access reachability from the server/client hosts.
- **Client cannot find the server**
  - Confirm `serverHost` is correct and that the server is listening on
    `5078`. The client uses `EPICS_PVA_NAME_SERVERS=<serverHost>:5078`.
- **Fontconfig cache version warning**
  - Harmless. `start_client.cmd` sets a private `XDG_CACHE_HOME` to suppress it.
- **Qt display/plugin errors on headless nodes**
  - Use an X-capable session, or for smoke tests only:
    `QT_QPA_PLATFORM=offscreen ./start_client.cmd`.

## Current Defaults

- Server channel: `masar_p4p`
- Client default channel: `masar_p4p`
- pvAccess server port: `5078`
- SQLite DB path: `./masar.db` (reference copy: `masar_example.db`)
