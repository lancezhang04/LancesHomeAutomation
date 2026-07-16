from datetime import time
from typing import override

from entities import Entity
from home import Home
from routines import Routine
from routines.time import TimeRoutine
from routines.transition import TransitionRoutine


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

    # TODO: Either make this timedelta based (for end time), or just a single call
    start_subroutine: TimeRoutine | None
    end_subroutine: TimeRoutine | None

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
            self.start_subroutine = TimeRoutine(
                home=self.home,
                service="set_light_state",
                call_time=self.start_time,
                weekdays=self.weekdays,
                entities=self.light,
                call_kwargs={"state": "on", "intensity": 100},
                # TODO: consider if "subroutine" is a good name
                name="Timed light on subroutine",
                description=f"Spawned by [{self.name}, TimedLight]",
            )
            self.start_subroutine.start()

        if self.end_time is not None:
            self.end_subroutine = TimeRoutine(
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


class TransitionLight(Routine):
    """
    Fade/transition the intensity of a light over a given period of time,
    on select or all weekdays
    """

    light: Entity
    start_time: time
    end_time: time
    start_intensity: float
    end_intensity: float
    weekdays: set[int] | None
    name: str
    description: str

    subroutine: TransitionRoutine

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
        self.light = light
        self.start_time = start_time
        self.end_time = end_time
        self.start_intensity = start_intensity
        self.end_intensity = end_intensity
        self.weekdays = weekdays

        super().__init__(home, name=name, description=description)

    @override
    def start(self) -> None:
        self.subroutine = TransitionRoutine(
            home=self.home,
            service="set_light_state",
            start_time=self.start_time,
            end_time=self.end_time,
            start_value=self.start_intensity,
            end_value=self.end_intensity,
            arg_name="intensity",
            entities=self.light,
            weekdays=self.weekdays,
            name="Transition light subroutine",
            description=f"Spawned by [{self.name}, TransitionLight]",
        )
        self.subroutine.start()
