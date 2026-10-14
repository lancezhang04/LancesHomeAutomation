"""
The routines that run in the apartment. Entity ids are friendly names in Zigbee2MQTT.

Preview a week of them with `python run_replay.py`.
"""

from datetime import time

from entities import Entity
from home import Home
from routines import TimedLight

WEEKDAYS = {0, 1, 2, 3, 4}  # Monday is 0

# Zigbee2MQTT group with kitchen_lamp, main_lamp and corner_lamp
all_lamps = Entity(id="all_lamps", type="light")


def start_routines(home: Home) -> None:
    TimedLight(
        home=home,
        light=all_lamps,
        start_time=time(6, 50),
        end_time=time(7, 40),
        weekdays=WEEKDAYS,
        name="Weekday morning lamps",
        description="On at 6:50, off at 7:40, Monday to Friday",
    ).start()

    TimedLight(
        home=home,
        light=all_lamps,
        start_time=time(17, 40),
        weekdays=WEEKDAYS,
        name="Weekday evening lamps",
        description="On at 17:40, Monday to Friday",
    ).start()
