from datetime import time, datetime
from typing import Any, override

from entities import Entity
from home import Home
from routines import Routine


class TimeRoutine(Routine):
    """
    Make a service call at a given time, on select or all weekdays
    """

    call_time: time
    weekdays: set[int] | None
    service: str
    entities: Entity | list[Entity] | None
    call_kwargs: dict[str, Any] | None

    def __init__(
        self,
        home: Home,
        service: str,
        call_time: time,
        weekdays: set[int] | None = None,
        entities: Entity | list[Entity] | None = None,
        call_kwargs: dict[str, Any] | None = None,
        name: str | None = None,
        description: str | None = None,
    ):
        self.service = service
        self.call_time = call_time
        self.weekdays = weekdays
        self.entities = entities
        self.call_kwargs = call_kwargs

        super().__init__(home, name=name, description=description)

    @override
    def on_time_change(self, current_time: datetime) -> None:
        if self.weekdays is None or current_time.weekday() in self.weekdays:
            # TODO: better method for checking time equivalence?
            if (
                current_time.hour == self.call_time.hour
                and current_time.minute == self.call_time.minute
            ):
                self.home.call(
                    service=self.service,
                    entities=self.entities,
                    call_kwargs=self.call_kwargs,
                )
