const EventType = {
    NODE_SELECTED: 'node_selected',
    ZOOM_CHANGED: 'zoom_changed',
    HTML_CHANGED: 'html_changed'
};

class Observer {
    constructor() {
        this._observers = {};
    }

    attach(eventType, observer) {
        if (!(eventType in this._observers)) {
            this._observers[eventType] = [];
        }
        this._observers[eventType].push(observer);
    }

    detach(eventType, observer) {
        if (eventType in this._observers) {
            const index = this._observers[eventType].indexOf(observer);
            if (index !== -1) {
                this._observers[eventType].splice(index, 1);
            }
        }
    }

    notify(eventType, data = null, data2 = null) {
        if (eventType in this._observers) {
            this._observers[eventType].forEach(observer => observer(eventType, data, data2));
        }
    }
}

let visualizer_observer = new VisualizerObserver();