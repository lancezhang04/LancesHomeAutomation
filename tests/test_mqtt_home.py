import pytest

from mqtt_home import zigbee2mqtt_payload


def test_light_on_off():
    assert zigbee2mqtt_payload("set_light_state", state="on") == {"state": "ON"}
    assert zigbee2mqtt_payload("set_light_state", state="off") == {"state": "OFF"}


def test_light_intensity_becomes_brightness():
    assert zigbee2mqtt_payload("set_light_state", state="on", intensity=100) == {
        "state": "ON",
        "brightness": 254,
    }
    assert zigbee2mqtt_payload("set_light_state", intensity=50) == {"brightness": 127}


def test_shade():
    assert zigbee2mqtt_payload("set_shade_state", state="open") == {"state": "OPEN"}


@pytest.mark.parametrize(
    "service, kwargs",
    [
        ("set_fan_speed", {"speed": 2}),
        ("set_light_state", {"state": "on", "color": "red"}),
        ("set_light_state", {}),
    ],
)
def test_rejects_bad_calls(service, kwargs):
    with pytest.raises(ValueError):
        zigbee2mqtt_payload(service, **kwargs)
