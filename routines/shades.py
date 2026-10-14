from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING, Literal

from entities import Entity
from routines.time import TimeRoutine

if TYPE_CHECKING:
    from home import Home


class TimedShade(TimeRoutine):
    """
    Open or close a shade at a given time, on select or all weekdays

    Idea: keep shade open/closed throughout the day depending on internal/external
    temperatures to save energy costs?
    """

    def __init__(
        self,
        home: Home,
        shade: Entity,
        call_time: time,
        state: Literal["open", "close"],
        weekdays: set[int] | None = None,
        name: str | None = None,
        description: str | None = None,
    ):
        super().__init__(
            home,
            service="set_shade_state",
            call_time=call_time,
            entities=shade,
            weekdays=weekdays,
            call_kwargs={"state": state},
            name=name,
            description=description,
        )
