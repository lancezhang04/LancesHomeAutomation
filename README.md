# LancesHomeAutomation

Home automation for the apartment: a Zigbee hub running on this Mac, plus Python routines that run on a schedule.

```
Sonoff ZBDongle-E ─ Zigbee2MQTT ─ Mosquitto (MQTT) ─ run_home.py (routines in automations.py)
                   (web UI at http://localhost:8080)
```

- **Zigbee2MQTT** (installed in `~/zigbee2mqtt`) talks to the dongle and the devices. Its config and extensions live in `hub/zigbee2mqtt/` and are symlinked into place.
- **Mosquitto** is the local message broker, reachable only from this Mac.
- **`run_home.py`** runs the routines in [automations.py](automations.py) on the real clock and sends commands through MQTT.
- **The button** is handled by [button-controls-lamps.mjs](hub/zigbee2mqtt/external_extensions/button-controls-lamps.mjs), which runs inside Zigbee2MQTT. The Sonoff SNZB-01P can't be bound directly to a group, so Zigbee2MQTT relays its presses instead. Single press: all lamps off if any are on, otherwise all on. Double: the lamps that are off turn on one by one in random order, 0.25–0.75 s apart. Long: all off. It's also editable in the web UI under Settings → Dev console → External Extensions.

## Layout

| Path | What it is |
| --- | --- |
| `automations.py` | The routines that run in the apartment |
| `entities/`, `routines/`, `home.py` | The routine framework |
| `mqtt_home.py` | Sends service calls to Zigbee2MQTT |
| `run_home.py` | Runs the routines for real (kept running by launchd) |
| `run_replay.py` | Prints what the routines would do over a simulated week |
| `hub/install.sh` | Sets up or re-applies the whole hub on this Mac |
| `hub/zigbee2mqtt/` | Zigbee2MQTT config, start script and extensions |
| `hub/mosquitto/` | Mosquitto config |
| `hub/git-hooks/pre-commit` | Blocks commits that would put a secret in the config |

## Setup

```bash
hub/install.sh
```

It installs what's missing (Mosquitto, Node 24, Python 3.13, Zigbee2MQTT), links the config files, enables the pre-commit check and (re)starts everything. Re-run it after changing anything in `hub/`. It's safe to run repeatedly.

The services run from this checkout, so whatever branch is checked out is what runs.

## Changing routines

Edit `automations.py`, then check and apply:

```bash
.venv/bin/python run_replay.py
```

```bash
.venv/bin/python -m pytest
```

```bash
launchctl kickstart -k gui/$(id -u)/com.lanceshomeautomation.routines
```

(Install the test dependencies once with `.venv/bin/pip install -r requirements-dev.txt`.)

## Changing the button

Edit [button-controls-lamps.mjs](hub/zigbee2mqtt/external_extensions/button-controls-lamps.mjs), then test it and restart Zigbee2MQTT to load it:

```bash
/opt/homebrew/opt/node@24/bin/node --test 'hub/zigbee2mqtt/tests/*.test.mjs'
```

```bash
launchctl kickstart -k gui/$(id -u)/com.zigbee2mqtt
```

Keep test files out of `external_extensions/`: Zigbee2MQTT loads every script in that folder as an extension.

## Changes made in the web UI

Renaming devices, editing groups or changing settings in the Zigbee2MQTT web UI writes straight into `hub/zigbee2mqtt/configuration.yaml`, so they show up in `git status`. Commit them like any other change. If you rename a device or group that a routine or the button extension uses, update the name there too.

## Secrets and backups

The repo is public, so the Zigbee network key is kept out of it: the config refers to it as `'!secret network_key'`, and the value lives in `~/zigbee2mqtt/data/secret.yaml`. The pre-commit hook refuses commits where `network_key`, `auth_token` or `password` in the config isn't a `!secret` reference.

The PAN IDs and device addresses in the config are not secret; every Zigbee radio nearby can already see them.

These files in `~/zigbee2mqtt/data` are not in git and are worth backing up somewhere private:

- `secret.yaml`: the network key
- `coordinator_backup.json`: the network's state (it contains the key too)
- `database.db`: the paired devices

To rebuild on another Mac: clone this repo, run `hub/install.sh` once (it stops and asks for `secret.yaml`), copy the three files above into `~/zigbee2mqtt/data`, plug in the dongle and run `hub/install.sh` again. Paired devices carry over without re-pairing.

## Logs

- Zigbee2MQTT: `~/zigbee2mqtt/data/log/` (a folder per start), and `launchd.log` there for crashes
- Routines: `~/Library/Logs/LancesHomeAutomation.log`
