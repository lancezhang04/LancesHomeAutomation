// Makes the Sonoff button (main_switch) control the all_lamps group.
// The button's firmware ignores group bindings, so Zigbee2MQTT relays its presses instead.
//   single press: all off if any lamp is on, otherwise all on
//   double press: the lamps that are off turn on one by one, in random order
//   long press:   all off
const BUTTON = "main_switch";
const GROUP = "all_lamps";
// Random pause between lamps on a double press
const MIN_DELAY_MS = 250;
const MAX_DELAY_MS = 750;

function shuffle(items) {
    for (let i = items.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [items[i], items[j]] = [items[j], items[i]];
    }
    return items;
}

export default class ButtonControlsLamps {
    constructor(zigbee, mqtt, state, publishEntityState, eventBus, enableDisableExtension, restartCallback, addExtension, settings, logger) {
        this.zigbee = zigbee;
        this.state = state;
        this.eventBus = eventBus;
        this.settings = settings;
        this.logger = logger;
        this.pending = [];
    }

    start() {
        this.eventBus.onPublishEntityState(this, (data) => this.onPublishEntityState(data));
    }

    stop() {
        this.cancelPending();
        this.eventBus.removeListeners(this);
    }

    onPublishEntityState({entity, payload}) {
        if (!entity.isDevice() || entity.name !== BUTTON || !payload?.action) return;

        const group = this.zigbee.resolveEntity(GROUP);
        if (!group) {
            this.logger.warning(`button-controls-lamps: group '${GROUP}' not found`);
            return;
        }

        // A new press overrides a one-by-one sequence that's still running
        this.cancelPending();

        if (payload.action === "single") this.setGroup(payload.action, this.members(group).some((lamp) => this.isOn(lamp)) ? "OFF" : "ON");
        else if (payload.action === "double") this.turnOnOneByOne(group);
        else if (payload.action === "long") this.setGroup(payload.action, "OFF");
    }

    setGroup(action, state) {
        this.logger.info(`button-controls-lamps: ${action} press -> ${GROUP} ${state}`);
        this.send(GROUP, state);
    }

    turnOnOneByOne(group) {
        const lamps = shuffle(this.members(group).filter((lamp) => !this.isOn(lamp)));
        this.logger.info(`button-controls-lamps: double press -> on one by one: ${lamps.map((lamp) => lamp.name).join(", ") || "(all already on)"}`);

        let at = 0;
        for (const [i, lamp] of lamps.entries()) {
            if (i > 0) at += MIN_DELAY_MS + Math.random() * (MAX_DELAY_MS - MIN_DELAY_MS);
            this.pending.push(setTimeout(() => this.send(lamp.name, "ON"), at));
        }
    }

    cancelPending() {
        for (const timer of this.pending) clearTimeout(timer);
        this.pending = [];
    }

    members(group) {
        const devices = group.zh.members.map((endpoint) => this.zigbee.resolveEntity(endpoint.getDevice()));
        return [...new Map(devices.filter(Boolean).map((device) => [device.name, device])).values()];
    }

    isOn(lamp) {
        return this.state.get(lamp).state === "ON";
    }

    send(name, state) {
        const baseTopic = this.settings.get().mqtt.base_topic;
        this.eventBus.emitMQTTMessage({topic: `${baseTopic}/${name}/set`, message: JSON.stringify({state})});
    }
}
