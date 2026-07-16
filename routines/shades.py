from datetime import time
from typing import override

from entities import Entity
from home import Home
from routines import Routine
from routines.base import TimedRoutine


class TimedShade(Routine):
    """
    Idea: keep shade open/closed throughout the day depending on internal/external
    temperatures to save energy costs?
    """

    shade: Entity  # TODO: change to Shade?
    call_time: time
    weekdays: set[int] | None
    state: str

    routine: Routine

    def __init__(
        self,
        home: Home,
        shade: Entity,
        call_time: time,
        state: str,
        weekdays: set[int] | None = None,
        name: str | None = None,
        description: str | None = None,
    ):
        self.shade = shade
        self.call_time = call_time
        self.state = state
        self.weekdays = weekdays

        super().__init__(home, name=name, description=description)

    @override
    def start(self) -> None:
        self.routine = TimedRoutine(
            home=self.home,
            service="set_shade_state",
            call_time=self.call_time,
            weekdays=self.weekdays,
            entities=self.shade,
            call_kwargs={"state": self.state},
            name=f"Timed shade {self.state} subroutine",
            description=f"Spawned by [{self.name}, TimedShade]",
        )
        self.routine.start()
