"""
Home that carries out service calls by sending commands to Zigbee2MQTT over MQTT
"""

from __future__ import annotations

import json
import logging
import threading
from typing import Any, override

import paho.mqtt.client as mqtt

from entities import Entity
from home import Home, as_list

log = logging.getLogger(__name__)

LIGHT_STATES = {"on": "ON", "off": "OFF"}
SHADE_STATES = {"open": "OPEN", "close": "CLOSE"}


def zigbee2mqtt_payload(service: str, **kwargs: Any) -> dict[str, Any]:
    """Translate a service call into the JSON that Zigbee2MQTT expects on `<entity>/set`."""
    payload: dict[str, Any] = {}
    if service == "set_light_state":
        if "state" in kwargs:
            payload["state"] = LIGHT_STATES[kwargs.pop("state")]
        if "intensity" in kwargs:
            # Zigbee brightness runs 0-254; intensity is a percentage
            payload["brightness"] = round(kwargs.pop("intensity") / 100 * 254)
    elif service == "set_shade_state":
        payload["state"] = SHADE_STATES[kwargs.pop("state")]
    else:
        raise ValueError(f"Unknown service: {service}")

    if kwargs:
        raise ValueError(f"Unexpected arguments for {service}: {kwargs}")
    if not payload:
        raise ValueError(f"Nothing to set for {service}")
    return payload


class MqttHome(Home):

    def __init__(
        self, host: str = "localhost", port: int = 1883, base_topic: str = "zigbee2mqtt"
    ) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.base_topic = base_topic

        self._connected = threading.Event()
        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id="lances-home-automation"
        )
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

    def connect(self, timeout: float = 10) -> None:
        """Connect in the background; paho keeps reconnecting if the broker goes away."""
        self._client.connect_async(self.host, self.port)
        self._client.loop_start()
        if not self._connected.wait(timeout):
            log.warning("No MQTT connection after %ss, still trying", timeout)

    def _on_connect(self, client, userdata, flags, reason_code, properties) -> None:
        if reason_code.is_failure:
            log.error("MQTT connection refused: %s", reason_code)
            return
        log.info("Connected to MQTT at %s:%s", self.host, self.port)
        self._connected.set()

    def _on_disconnect(self, client, userdata, flags, reason_code, properties) -> None:
        self._connected.clear()
        log.warning("Disconnected from MQTT (%s), reconnecting", reason_code)

    @override
    def call(self, service: str, entities: Entity | list[Entity], **kwargs: Any) -> None:
        payload = json.dumps(zigbee2mqtt_payload(service, **kwargs))
        for entity in as_list(entities):
            topic = f"{self.base_topic}/{entity.id}/set"
            if not self._connected.is_set():
                # Don't queue it: a command sent late (an "on" meant for 6:50 arriving at 9:00)
                # is worse than none
                log.error("Not connected to MQTT, dropped %s %s", topic, payload)
                continue
            self._client.publish(topic, payload, qos=1)
            log.info("%s %s", topic, payload)
