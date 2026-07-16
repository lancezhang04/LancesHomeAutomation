"""
Simulate a week worth of events, display all calls from routines
"""

from datetime import datetime, time

from home import FakeHome
from entities import Entity
from routines.lights import TransitionLight

home = FakeHome(
    config_path="",
    # Starting at midnight on a Monday
    start_time=datetime(2026, 7, 13, 0, 0, 0),
)

TransitionLight(
    home=home,
    light=Entity(id="bedroom_light", type="light"),
    start_time=time(8, 0),
    end_time=time(8, 10),
    start_intensity=0,
    end_intensity=100,
    weekdays={0},
).start()

# TimedLight(
#     home=home,
#     light=Entity(id="test_light", type="light"),
#     start_time=time(7, 30),
#     end_time=time(9, 30),
#     weekdays={0, 1, 2, 3, 4},
#     name="Weekday morning lights",
#     description="Turns off after two hours to save energy",
# ).start()
#
# TimedLight(
#     home=home,
#     light=Entity(id="test_light", type="light"),
#     start_time=time(9, 30),
#     end_time=time(10, 0),
#     weekdays={5, 6},
#     name="Weekend morning lights",
#     description="Two hours later than usual",
# ).start()
#
# TimedShade(
#     home=home,
#     shade=Entity(id="test_shade", type="shade"),
#     call_time=time(7, 0),
#     weekdays={0, 1, 2, 3, 4},
#     state="open",
#     name="Weekday morning shade",
# ).start()

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
