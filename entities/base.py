from dataclasses import dataclass
from typing import Literal

EntityType = Literal["light", "shade"]


# TODO: decide whether entities should carry state (e.g. is this shade open?). A stored value
# can't be trusted later (manual adjustment, reboot), so the ground truth has to come from the
# devices themselves, i.e. through the Home.
@dataclass(frozen=True)
class Entity:
    """A device or group that routines control. `id` is its friendly name in Zigbee2MQTT."""

    id: str
    type: EntityType
