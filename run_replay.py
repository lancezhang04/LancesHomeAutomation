"""
Simulate a week of the routines in automations.py, display all calls they make
"""

from datetime import datetime

from automations import start_routines
from home import FakeHome

home = FakeHome(
    # Starting at midnight on a Monday
    start_time=datetime(2026, 7, 13, 0, 0, 0),
)
start_routines(home)

home.describe_routines()

for weekday in [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]:
    print(weekday)
    for _ in range(1 * 24 * 60):
        home.tick()
    print()
