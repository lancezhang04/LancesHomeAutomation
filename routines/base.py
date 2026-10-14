from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from home import Home


class Routine:

    home: Home
    name: str | None
    description: str | None

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
