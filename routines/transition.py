from __future__ import annotations

from datetime import date, datetime, time
from typing import TYPE_CHECKING, override

from entities import Entity
from routines.base import Routine

if TYPE_CHECKING:
    from home import Home


def _seconds_between(start: time, end: time) -> float:
    return (datetime.combine(date.min, end) - datetime.combine(date.min, start)).total_seconds()


class TransitionRoutine(Routine):
    """
    Call a service with a range of values in a given time period,
    on select or all weekdays (Monday is 0)

    This is useful for routines such as fading in and out lights
    """

    start_time: time
    end_time: time
    start_value: float
    end_value: float
    rounding: str | None
    weekdays: set[int] | None

    service: str
    arg_name: str
    entities: Entity | list[Entity]

    def __init__(
        self,
        home: Home,
        service: str,
        start_time: time,
        end_time: time,
        start_value: float,
        end_value: float,
        arg_name: str,
        entities: Entity | list[Entity],
        rounding: str | None = None,
        weekdays: set[int] | None = None,
        name: str | None = None,
        description: str | None = None,
    ):
        if end_time <= start_time:
            raise ValueError("end_time must be after start_time")
        if rounding is not None and rounding != "int":
            raise ValueError(f"Unrecognized rounding value: {rounding}")

        self.service = service
        self.start_time = start_time
        self.end_time = end_time
        self.start_value = start_value
        self.end_value = end_value
        self.arg_name = arg_name
        self.entities = entities
        self.rounding = rounding
        self.weekdays = weekdays

        super().__init__(home, name=name, description=description)

    @override
    def on_time_change(self, current_time: datetime) -> None:
        if self.weekdays is not None and current_time.weekday() not in self.weekdays:
            return
        timestamp = current_time.time()
        if not self.start_time <= timestamp <= self.end_time:
            return

        progress = _seconds_between(self.start_time, timestamp) / _seconds_between(
            self.start_time, self.end_time
        )
        current_value = self.start_value + progress * (self.end_value - self.start_value)
        if self.rounding == "int":
            current_value = round(current_value)

        self.home.call(self.service, self.entities, **{self.arg_name: current_value})
