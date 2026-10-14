from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, override

from entities import Entity

if TYPE_CHECKING:
    from routines import Routine


def as_list(entities: Entity | list[Entity]) -> list[Entity]:
    return entities if isinstance(entities, list) else [entities]


class Home:
    """Holds the running routines and carries out the service calls they make."""

    routines: list[Routine]

    def __init__(self) -> None:
        self.routines = []

    def on_time_change(self, current_time: datetime) -> None:
        for routine in self.routines:
            routine.on_time_change(current_time)

    def call(self, service: str, entities: Entity | list[Entity], **kwargs: Any) -> None:
        raise NotImplementedError

    def describe_routines(self) -> None:
        no_doc_count = 0
        for routine in self.routines:
            if routine.name is None and routine.description is None:
                no_doc_count += 1
            else:
                print(f"Name: {routine.name}\nDescription: {routine.description}\n")

        if no_doc_count > 0:
            print(f"{no_doc_count} routine(s) without name or description\n")


@dataclass(frozen=True)
class Call:
    time: datetime
    service: str
    entities: list[Entity]
    kwargs: dict[str, Any]


class FakeHome(Home):
    """Records service calls instead of making them, for replaying routines on a simulated clock."""

    current_time: datetime
    calls: list[Call]

    def __init__(self, start_time: datetime | None = None, verbose: bool = True) -> None:
        super().__init__()
        self.current_time = start_time if start_time is not None else datetime.now()
        self.calls = []
        self.verbose = verbose

    def tick(self, tick_size: timedelta = timedelta(minutes=1)) -> None:
        self.current_time += tick_size
        self.on_time_change(self.current_time)

    @override
    def call(self, service: str, entities: Entity | list[Entity], **kwargs: Any) -> None:
        call = Call(self.current_time, service, as_list(entities), kwargs)
        self.calls.append(call)
        if self.verbose:
            names = ", ".join(entity.id for entity in call.entities)
            print(f"[{call.time:%a %H:%M}] {service} | {names} | {kwargs}")
