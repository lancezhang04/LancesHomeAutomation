"""
Run the routines in automations.py against the real devices, through Zigbee2MQTT.
launchd keeps this running (see hub/install.sh).
"""

import logging
import time
from collections.abc import Iterator
from datetime import datetime, timedelta

from automations import start_routines
from mqtt_home import MqttHome

ONE_MINUTE = timedelta(minutes=1)
# After a longer gap (e.g. the Mac was asleep), skip the missed minutes instead of replaying them late
MAX_CATCH_UP = timedelta(minutes=5)

log = logging.getLogger("run_home")


def minutes_to_process(last: datetime, now: datetime) -> Iterator[datetime]:
    """Each whole minute after `last`, up to and including `now`, going back at most MAX_CATCH_UP."""
    if now - last > MAX_CATCH_UP:
        log.warning("Clock jumped from %s to %s, skipping missed minutes", last, now)
        last = now - MAX_CATCH_UP
    minute = last + ONE_MINUTE
    while minute <= now:
        yield minute
        minute += ONE_MINUTE


def current_minute() -> datetime:
    return datetime.now().replace(second=0, microsecond=0)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    home = MqttHome()
    start_routines(home)
    for routine in home.routines:
        log.info("Loaded routine: %s", routine.name)
    home.connect()

    # Start one minute back so the current minute runs too: a restart at 6:50 still turns lamps on
    last = current_minute() - ONE_MINUTE
    while True:
        now = current_minute()
        for minute in minutes_to_process(last, now):
            home.on_time_change(minute)
        last = now
        # Wake just after the next minute starts
        time.sleep((now + ONE_MINUTE - datetime.now()).total_seconds() + 0.5)


if __name__ == "__main__":
    main()
