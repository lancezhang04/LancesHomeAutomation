from datetime import datetime, timedelta

from entities.base import Entity
from typing import override


class Home:

    # TODO: Dictionary mapping entity ID to entities
    entities: dict[str, Entity]
    routines: list[...]

    def __init__(self, config_path: str) -> None:
        self.entities = dict()
        self.routines = list()

        # TODO: use config to load entities (and possibly routines)

    def on_time_change(self, current_time: datetime) -> None:
        for routine in self.routines:
            routine.on_time_change(current_time)

    # TODO: Not exactly sure how to structure this yet
    def call(
        self, service: str, entities: Entity | list[Entity] | None, **kwargs
    ) -> None:
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


class FakeHome(Home):

    current_time: datetime

    def __init__(self, config_path: str, start_time: datetime | None) -> None:
        self.current_time = start_time if start_time is not None else datetime.now()

        super().__init__(config_path)

    def tick(self, tick_size: timedelta = timedelta(minutes=1)) -> None:
        self.current_time += tick_size
        self.on_time_change(self.current_time)

    @override
    def call(
        self, service: str, entities: Entity | list[Entity] | None, **kwargs
    ) -> None:
        # TODO: how does vim surround work again lol
        print(f"[{self.current_time}] {service} | {entities} | {kwargs}")
