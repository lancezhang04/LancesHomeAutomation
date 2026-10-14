from datetime import datetime

from automations import all_lamps, start_routines
from home import FakeHome


def test_weekday_lamp_schedule():
    # Midnight on a Monday, then one simulated week
    home = FakeHome(start_time=datetime(2026, 10, 12, 0, 0), verbose=False)
    start_routines(home)
    for _ in range(7 * 24 * 60):
        home.tick()

    expected = [
        (f"{day} {at}", state)
        for day in ["Mon", "Tue", "Wed", "Thu", "Fri"]
        for at, state in [("06:50", "on"), ("07:40", "off"), ("17:40", "on")]
    ]
    assert [(f"{call.time:%a %H:%M}", call.kwargs["state"]) for call in home.calls] == expected
    assert all(call.service == "set_light_state" for call in home.calls)
    assert all(call.entities == [all_lamps] for call in home.calls)
