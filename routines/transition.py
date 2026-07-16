from datetime import time, datetime, timedelta

from entities import Entity
from home import Home
from routines import Routine


class TransitionRoutine(Routine):
    """
    Call a service with a range of values in a given time period,
    on select or all weekdays

    This is useful for routines such as fading in and out lights
    """

    start_time: time
    end_time: time
    start_value: float
    end_value: float
    interval: float
    rounding: str | None
    weekdays: set[int] | None

    service: str
    arg_name: str
    entities: Entity | list[Entity] | None

    def __init__(
        self,
        home: Home,
        service: str,
        start_time: time,
        end_time: time,
        start_value: float,
        end_value: float,
        arg_name: str,
        entities: Entity | list[Entity] | None,
        rounding: str | None = None,
        weekdays: set[int] | None = None,
        name: str | None = None,
        description: str | None = None,
    ):
        if end_time <= start_time:
            raise ValueError("end_time must be after start_time")
        if rounding is not None and rounding != "int":
            raise ValueError(f"Unrecognized rounding value: {rounding}")

        self.service = service
        self.start_time = start_time
        self.end_time = end_time
        self.start_value = start_value
        self.end_value = end_value
        self.arg_name = arg_name
        self.entities = entities
        self.rounding = rounding
        self.weekdays = weekdays

        # TODO: how to better take different between time?
        self.interval = timedelta(
            hours=self.end_time.hour - self.start_time.hour,
            minutes=self.end_time.minute - self.start_time.minute,
        ).seconds

        super().__init__(home, name=name, description=description)

    def on_time_change(self, current_time: datetime) -> None:
        if self.weekdays is None or current_time.weekday() in self.weekdays:
            timestamp = current_time.time()
            if self.start_time <= timestamp <= self.end_time:
                elapsed = timedelta(
                    hours=timestamp.hour - self.start_time.hour,
                    minutes=timestamp.minute - self.start_time.minute,
                ).seconds

                current_value = (
                    elapsed / self.interval * (self.end_value - self.start_value)
                    + self.start_value
                )
                if self.rounding == "int":
                    current_value = round(current_value)

                self.home.call(
                    service=self.service,
                    entities=self.entities,
                    call_kwargs={
                        self.arg_name: current_value,
                    },
                )
