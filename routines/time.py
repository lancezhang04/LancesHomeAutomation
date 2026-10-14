from __future__ import annotations

from datetime import datetime, time
from typing import TYPE_CHECKING, Any, override

from entities import Entity
from routines.base import Routine

if TYPE_CHECKING:
    from home import Home


class TimeRoutine(Routine):
    """
    Make a service call at a given time, on select or all weekdays (Monday is 0)
    """

    call_time: time
    weekdays: set[int] | None
    service: str
    entities: Entity | list[Entity]
    call_kwargs: dict[str, Any]

    def __init__(
        self,
        home: Home,
        service: str,
        call_time: time,
        entities: Entity | list[Entity],
        weekdays: set[int] | None = None,
        call_kwargs: dict[str, Any] | None = None,
        name: str | None = None,
        description: str | None = None,
    ):
        self.service = service
        self.call_time = call_time
        self.entities = entities
        self.weekdays = weekdays
        self.call_kwargs = call_kwargs if call_kwargs is not None else {}

        super().__init__(home, name=name, description=description)

    @override
    def on_time_change(self, current_time: datetime) -> None:
        if self.weekdays is not None and current_time.weekday() not in self.weekdays:
            return
        # The clock moves in whole minutes, so matching the minute fires exactly once
        if (current_time.hour, current_time.minute) == (self.call_time.hour, self.call_time.minute):
            self.home.call(self.service, self.entities, **self.call_kwargs)
