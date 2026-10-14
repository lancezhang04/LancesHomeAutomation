from __future__ import annotations

from datetime import datetime, time
from typing import TYPE_CHECKING, Any, override

from entities import Entity
from routines.base import Routine
from routines.time import TimeRoutine
from routines.transition import TransitionRoutine

if TYPE_CHECKING:
    from home import Home


class TimedLight(Routine):
    """
    Turn a light on and/or off at given times, on select or all weekdays
    We bundle turning on and off the light since we often want to turn a light off
    soon after we turn it on (e.g., on a weekday morning)
    """

    light: Entity
    steps: list[TimeRoutine]

    def __init__(
        self,
        home: Home,
        light: Entity,
        start_time: time | None = None,
        end_time: time | None = None,
        weekdays: set[int] | None = None,
        intensity: float | None = None,
        name: str | None = None,
        description: str | None = None,
    ) -> None:
        if start_time is None and end_time is None:
            raise ValueError("Either start_time or end_time is required")

        super().__init__(home, name=name, description=description)
        self.light = light
        self.steps = []

        if start_time is not None:
            on_kwargs: dict[str, Any] = {"state": "on"}
            if intensity is not None:
                on_kwargs["intensity"] = intensity
            self.steps.append(
                TimeRoutine(home, "set_light_state", start_time, light, weekdays, on_kwargs)
            )
        if end_time is not None:
            self.steps.append(
                TimeRoutine(home, "set_light_state", end_time, light, weekdays, {"state": "off"})
            )

    @override
    def on_time_change(self, current_time: datetime) -> None:
        for step in self.steps:
            step.on_time_change(current_time)


class TransitionLight(TransitionRoutine):
    """
    Fade/transition the intensity of a light over a given period of time,
    on select or all weekdays
    """

    def __init__(
        self,
        home: Home,
        light: Entity,
        start_time: time,
        end_time: time,
        start_intensity: float,
        end_intensity: float,
        weekdays: set[int] | None = None,
        name: str | None = None,
        description: str | None = None,
    ):
        super().__init__(
            home,
            service="set_light_state",
            start_time=start_time,
            end_time=end_time,
            start_value=start_intensity,
            end_value=end_intensity,
            arg_name="intensity",
            entities=light,
            weekdays=weekdays,
            name=name,
            description=description,
        )
