from datetime import time, datetime
from typing import override

from entities.base import Entity
from home import Home
from routines.base import Routine


# TODO: refactor into TimedRoutine -> TimedLight, TimedShade, TimedMusic, etc.
class TimedLight(Routine):
    """
    Turn a light on and/or off at given times, on select or all weekdays
    """

    light: Entity  # TODO: change to light entity?
    start_time: time | None
    end_time: time | None
    weekdays: set[int] | None

    def __init__(
        self,
        home: Home,
        light: Entity,
        start_time: time | None = None,
        end_time: time | None = None,
        weekdays: set[int] | None = None,
        name: str | None = None,
        description: str | None = None,
    ) -> None:
        if start_time is None and end_time is None:
            raise ValueError("Either start_time or end_time is required")

        self.light = light
        self.start_time = start_time
        self.end_time = end_time
        self.weekdays = weekdays

        super().__init__(home, name=name, description=description)

    @override
    def on_time_change(self, current_time: datetime) -> None:
        if self.weekdays is None or current_time.weekday() in self.weekdays:
            # TODO: better method for checking time equivalence?
            if (
                current_time.hour == self.start_time.hour
                and current_time.minute == self.start_time.minute
            ):
                self.home.call(
                    service="set_light_state",
                    entities=self.light,
                    state=True,
                )

            if (
                current_time.hour == self.end_time.hour
                and current_time.minute == self.end_time.minute
            ):
                self.home.call(
                    service="set_light_state",
                    entities=self.light,
                    state=False,
                )
