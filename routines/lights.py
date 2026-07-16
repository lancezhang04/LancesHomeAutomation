from datetime import time
from typing import override

from entities import Entity
from home import Home
from routines import Routine
from routines.base import TimedRoutine


class TimedLight(Routine):
    """
    Turn a light on and/or off at given times, on select or all weekdays
    We bundle turning on and off the light since we often want to turn a light off
    soon after we turn it on (e.g., on a weekday morning)
    """

    light: Entity  # TODO: change to light entity?
    start_time: time | None
    end_time: time | None
    weekdays: set[int] | None

    start_subroutine: TimedRoutine | None
    end_subroutine: TimedRoutine | None

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
    def start(self) -> None:
        if self.start_time is not None:
            self.start_subroutine = TimedRoutine(
                home=self.home,
                service="set_light_state",
                call_time=self.start_time,
                weekdays=self.weekdays,
                entities=self.light,
                call_kwargs={"state": "on"},
                # TODO: consider if "subroutine" is a good name
                name="Timed light on subroutine",
                description=f"Spawned by [{self.name}, TimedLight]",
            )
            self.start_subroutine.start()

        if self.end_time is not None:
            self.end_subroutine = TimedRoutine(
                home=self.home,
                service="set_light_state",
                call_time=self.end_time,
                weekdays=self.weekdays,
                entities=self.light,
                call_kwargs={"state": "off"},
                name="Timed light off subroutine",
                description=f"Spawned by [{self.name}, TimedLight]",
            )
            self.end_subroutine.start()
