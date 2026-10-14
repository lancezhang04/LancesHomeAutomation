// Makes the Sonoff button (main_switch) control the all_lamps group.
// The button's firmware ignores group bindings, so Zigbee2MQTT relays its presses instead.
//   single press: all off if any lamp is on, otherwise all on
//   double press: all on
//   long press:   all off
const BUTTON = "main_switch";
const GROUP = "all_lamps";

export default class ButtonControlsLamps {
    constructor(zigbee, mqtt, state, publishEntityState, eventBus, enableDisableExtension, restartCallback, addExtension, settings, logger) {
        this.zigbee = zigbee;
        this.state = state;
        this.eventBus = eventBus;
        this.settings = settings;
        this.logger = logger;
    }

    start() {
        this.eventBus.onPublishEntityState(this, (data) => this.onPublishEntityState(data));
    }

    stop() {
        this.eventBus.removeListeners(this);
    }

    onPublishEntityState({entity, payload}) {
        if (!entity.isDevice() || entity.name !== BUTTON || !payload?.action) return;

        const group = this.zigbee.resolveEntity(GROUP);
        if (!group) {
            this.logger.warning(`button-controls-lamps: group '${GROUP}' not found`);
            return;
        }

        let state;
        if (payload.action === "single") state = this.anyMemberOn(group) ? "OFF" : "ON";
        else if (payload.action === "double") state = "ON";
        else if (payload.action === "long") state = "OFF";
        else return;

        this.logger.info(`button-controls-lamps: ${payload.action} press -> ${GROUP} ${state}`);
        const baseTopic = this.settings.get().mqtt.base_topic;
        this.eventBus.emitMQTTMessage({topic: `${baseTopic}/${GROUP}/set`, message: JSON.stringify({state})});
    }

    anyMemberOn(group) {
        return group.zh.members.some((endpoint) => {
            const device = this.zigbee.resolveEntity(endpoint.getDevice());
            return device !== undefined && this.state.get(device).state === "ON";
        });
    }
}
