from datetime import datetime

from run_home import minutes_to_process


def at(hour: int, minute: int) -> datetime:
    return datetime(2026, 10, 12, hour, minute)


def test_next_minute():
    assert list(minutes_to_process(at(6, 49), at(6, 50))) == [at(6, 50)]


def test_short_gap_is_caught_up():
    assert list(minutes_to_process(at(6, 48), at(6, 51))) == [at(6, 49), at(6, 50), at(6, 51)]


def test_long_gap_only_replays_the_last_few_minutes():
    assert list(minutes_to_process(at(5, 0), at(9, 0))) == [
        at(8, 56),
        at(8, 57),
        at(8, 58),
        at(8, 59),
        at(9, 0),
    ]


def test_clock_going_back_runs_nothing():
    assert list(minutes_to_process(at(2, 0), at(1, 0))) == []
