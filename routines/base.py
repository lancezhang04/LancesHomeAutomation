from datetime import datetime
from typing import Any

from home import Home


class Routine:

    # TODO: change typing to include real HOME adapter
    home: Home
    name: str | None
    description: str | None

    # TODO: should we even specify a return type here?
    def __init__(
        self,
        home: Home,
        name: str | None = None,
        description: str | None = None,
    ) -> None:
        self.home = home
        self.name = name
        self.description = description

    def on_time_change(self, current_time: datetime) -> None:
        pass

    def on_event(self, event: Any) -> None:
        pass

    def start(self) -> None:
        self.home.routines.append(self)

    def stop(self) -> None:
        self.home.routines.remove(self)

    # TODO: add ability to skip for the next day, activation, etc. (e.g., overridden by one-off alarms)
