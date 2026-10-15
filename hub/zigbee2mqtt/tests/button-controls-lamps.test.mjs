// Run with: /opt/homebrew/opt/node@24/bin/node --test hub/zigbee2mqtt/tests/
import assert from "node:assert/strict";
import {beforeEach, mock, test} from "node:test";

import ButtonControlsLamps from "../external_extensions/button-controls-lamps.mjs";

let sent; // [{at, topic, state}]
let lampStates;
let press;

function setup(states) {
    lampStates = states;
    sent = [];
    const lamps = Object.keys(states).map((name) => ({name, zh: {name}}));
    const group = {name: "all_lamps", zh: {members: lamps.map((lamp) => ({getDevice: () => lamp.zh}))}};
    const zigbee = {
        resolveEntity: (key) => (key === "all_lamps" ? group : lamps.find((lamp) => lamp.zh === key)),
    };
    const eventBus = {
        onPublishEntityState: (_key, callback) => {
            press = (action) => callback({entity: {name: "main_switch", isDevice: () => true}, payload: {action}});
        },
        emitMQTTMessage: ({topic, message}) => sent.push({at: Date.now(), topic, state: JSON.parse(message).state}),
        removeListeners: () => {},
    };
    const state = {get: (device) => ({state: lampStates[device.name]})};
    const settings = {get: () => ({mqtt: {base_topic: "zigbee2mqtt"}})};
    const logger = {info: () => {}, warning: () => {}};
    const extension = new ButtonControlsLamps(zigbee, null, state, null, eventBus, null, null, null, settings, logger);
    extension.start();
    return extension;
}

beforeEach(() => {
    mock.timers.reset();
    mock.timers.enable({apis: ["setTimeout", "Date"], now: 0});
});

// One big tick() moves Date.now() to the end before running the timers, so step 1 ms at a time
// when the time each message was sent matters
function advance(ms) {
    mock.timers.tick(0);
    for (let i = 0; i < ms; i++) mock.timers.tick(1);
}

test("double press turns the off lamps on one at a time, with 250-750 ms between them", () => {
    setup({kitchen_lamp: "OFF", main_lamp: "OFF", corner_lamp: "OFF"});
    press("double");
    advance(2_000);

    assert.deepEqual(sent.map((s) => s.topic).sort(), [
        "zigbee2mqtt/corner_lamp/set",
        "zigbee2mqtt/kitchen_lamp/set",
        "zigbee2mqtt/main_lamp/set",
    ]);
    assert.ok(sent.every((s) => s.state === "ON"));
    assert.equal(sent[0].at, 0);
    for (let i = 1; i < sent.length; i++) {
        const gap = sent[i].at - sent[i - 1].at;
        assert.ok(gap >= 249 && gap <= 751, `gap ${gap} ms`); // ±1 ms: the clock steps in whole ms
    }
});

test("double press skips lamps that are already on", () => {
    setup({kitchen_lamp: "ON", main_lamp: "OFF", corner_lamp: "ON"});
    press("double");
    mock.timers.tick(10_000);
    assert.deepEqual(sent.map((s) => s.topic), ["zigbee2mqtt/main_lamp/set"]);
});

test("double press shuffles the order", () => {
    const orders = new Set();
    for (let run = 0; run < 50; run++) {
        setup({kitchen_lamp: "OFF", main_lamp: "OFF", corner_lamp: "OFF"});
        press("double");
        mock.timers.tick(10_000);
        orders.add(sent.map((s) => s.topic).join());
    }
    assert.ok(orders.size > 1, "always the same order");
});

test("a long press cancels lamps still waiting to turn on", () => {
    setup({kitchen_lamp: "OFF", main_lamp: "OFF", corner_lamp: "OFF"});
    press("double");
    mock.timers.tick(0); // first lamp on
    press("long");
    mock.timers.tick(10_000);
    assert.equal(sent.length, 2);
    assert.deepEqual(sent[1], {at: 0, topic: "zigbee2mqtt/all_lamps/set", state: "OFF"});
});

test("single press turns all off if any lamp is on", () => {
    setup({kitchen_lamp: "OFF", main_lamp: "ON", corner_lamp: "OFF"});
    press("single");
    assert.deepEqual(sent, [{at: 0, topic: "zigbee2mqtt/all_lamps/set", state: "OFF"}]);
});

test("single press turns all on if every lamp is off", () => {
    setup({kitchen_lamp: "OFF", main_lamp: "OFF", corner_lamp: "OFF"});
    press("single");
    assert.deepEqual(sent, [{at: 0, topic: "zigbee2mqtt/all_lamps/set", state: "ON"}]);
});
