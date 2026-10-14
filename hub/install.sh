#!/bin/zsh
# Sets up the Zigbee hub on this Mac from this repo, or re-applies it after changes. Safe to re-run.
#
# Zigbee2MQTT's config and extensions, and Mosquitto's config, become symlinks to the files in hub/,
# so changes made in the Zigbee2MQTT web page show up here as git changes. Secrets and runtime data
# (secret.yaml, database.db, coordinator_backup.json, logs) stay in ~/zigbee2mqtt/data.
set -euo pipefail

REPO=${0:A:h:h}
HUB=$REPO/hub
Z2M=$HOME/zigbee2mqtt
DATA=$Z2M/data
NODE_BIN=/opt/homebrew/opt/node@24/bin
AGENTS=$HOME/Library/LaunchAgents
DOMAIN=gui/$(id -u)

step() { print -P "%F{cyan}==>%f $*" }

# Replaces $2 with a symlink to $1, moving aside whatever was there
link() {
  local src=$1 dst=$2
  [[ -L $dst && $(readlink $dst) == $src ]] && return
  if [[ -e $dst || -L $dst ]]; then
    local backup=$dst.bak-$(date +%Y%m%d-%H%M%S)
    mv $dst $backup
    echo "    moved the old $dst to $backup"
  fi
  ln -s $src $dst
  echo "    linked $dst"
}

# Writes a launchd agent that starts $3... at login and keeps it running, then (re)starts it
agent() {
  local label=$1 log=$2; shift 2
  local args=""
  for arg in "$@"; do args+="<string>$arg</string>"; done
  cat > $AGENTS/$label.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$label</string>
  <key>ProgramArguments</key><array>$args</array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ThrottleInterval</key><integer>15</integer>
  <key>StandardOutPath</key><string>$log</string>
  <key>StandardErrorPath</key><string>$log</string>
</dict>
</plist>
EOF
  launchctl bootout $DOMAIN/$label 2>/dev/null || true
  while launchctl print $DOMAIN/$label >/dev/null 2>&1; do sleep 0.2; done
  launchctl bootstrap $DOMAIN $AGENTS/$label.plist
  echo "    (re)started $label"
}

step "Homebrew packages"
for formula in mosquitto node@24 python@3.13; do
  brew list $formula >/dev/null 2>&1 || brew install $formula
done

if [[ ! -f $Z2M/index.js ]]; then
  step "Installing Zigbee2MQTT into $Z2M"
  git clone --depth 1 https://github.com/Koenkk/zigbee2mqtt.git $Z2M
  # Use the exact pnpm version Zigbee2MQTT pins (corepack's copy can have stale signing keys)
  pnpm=$($NODE_BIN/node -p "require('$Z2M/package.json').packageManager")
  (cd $Z2M && PATH=$NODE_BIN:$PATH npx --yes $pnpm install --frozen-lockfile && PATH=$NODE_BIN:$PATH npx --yes $pnpm run build)
fi

step "Zigbee network key"
mkdir -p $DATA/log
if [[ ! -f $DATA/secret.yaml ]]; then
  if [[ -f $DATA/configuration.yaml && ! -L $DATA/configuration.yaml ]]; then
    # First run on a machine whose config still holds the key: move the key out into secret.yaml
    (cd $Z2M && $NODE_BIN/node -e '
      const yaml = require("js-yaml"), fs = require("fs");
      const key = yaml.load(fs.readFileSync(process.argv[1], "utf8")).advanced?.network_key;
      if (!Array.isArray(key)) { console.error("No network key in " + process.argv[1]); process.exit(1); }
      fs.writeFileSync(process.argv[2], yaml.dump({network_key: key}), {mode: 0o600});
    ' $DATA/configuration.yaml $DATA/secret.yaml)
    echo "    moved the network key from configuration.yaml into secret.yaml"
  else
    echo "Missing $DATA/secret.yaml. Restore it from a backup (see README.md)." >&2
    echo "Only for a brand-new Zigbee network, create it containing:  network_key: GENERATE" >&2
    exit 1
  fi
fi
chmod 600 $DATA/secret.yaml
(cd $Z2M && $NODE_BIN/node -e '
  const key = require("js-yaml").load(require("fs").readFileSync(process.argv[1], "utf8")).network_key;
  const ok = key === "GENERATE" || (Array.isArray(key) && key.length === 16 && key.every(Number.isInteger));
  if (!ok) { console.error("network_key in " + process.argv[1] + " should be 16 numbers"); process.exit(1); }
' $DATA/secret.yaml)
echo "    secret.yaml is valid"

step "Python environment"
[[ -x $REPO/.venv/bin/python ]] || /opt/homebrew/bin/python3.13 -m venv $REPO/.venv
$REPO/.venv/bin/pip install --quiet --disable-pip-version-check -r $REPO/requirements.txt
echo "    $REPO/.venv is ready"

step "Linking config files to the repo"
link $HUB/zigbee2mqtt/configuration.yaml $DATA/configuration.yaml
link $HUB/zigbee2mqtt/external_extensions $DATA/external_extensions
link $HUB/mosquitto/mosquitto.conf /opt/homebrew/etc/mosquitto/mosquitto.conf
git -C $REPO config core.hooksPath hub/git-hooks
echo "    enabled the pre-commit check for secrets"

step "Starting services"
brew services restart mosquitto >/dev/null
echo "    (re)started mosquitto"
agent com.zigbee2mqtt $DATA/log/launchd.log $HUB/zigbee2mqtt/start.sh
agent com.lanceshomeautomation.routines $HOME/Library/Logs/LancesHomeAutomation.log \
  $REPO/.venv/bin/python $REPO/run_home.py

step "Waiting for Zigbee2MQTT"
# Each Zigbee2MQTT start logs into a new folder; only trust one created after this restart
for _ in {1..30}; do
  run_dir=$(ls -dt $DATA/log/*/ 2>/dev/null | head -1)
  if [[ -n $run_dir && $run_dir -nt $AGENTS/com.zigbee2mqtt.plist ]] && grep -q "Zigbee2MQTT started" ${run_dir}log.log 2>/dev/null; then
    grep -E "INIT TC|external extension|Zigbee2MQTT started" ${run_dir}log.log | sed -E 's/\x1b\[[0-9;]*m//g; s/^/    /'
    exit 0
  fi
  sleep 2
done
echo "Zigbee2MQTT didn't report it started within a minute. Check $DATA/log/launchd.log and the newest log in $DATA/log/" >&2
exit 1
