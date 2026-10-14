#!/bin/zsh
# Runs Zigbee2MQTT. launchd starts this and restarts it if it exits (see hub/install.sh).
# Finds the Sonoff dongle's current serial port first, because the /dev/cu.usbserial-* name
# changes when the dongle is moved to another USB port.
port=$(ioreg -r -l -n "Sonoff Zigbee 3.0 USB Dongle Plus V2" | awk -F'"' '/IOCalloutDevice/{print $4; exit}')
if [[ -z "$port" ]]; then
  echo "$(date) Sonoff dongle not found; launchd will retry" >&2
  exit 1
fi
export ZIGBEE2MQTT_CONFIG_SERIAL_PORT="$port"
cd "$HOME/zigbee2mqtt"
exec /opt/homebrew/opt/node@24/bin/node index.js
