/**
 * state.js
 * Central frontend state store.
 * All JS files read/write workspace state through this object
 * instead of using their own globals.
 */

const State = {
    _currentWorkspaceId: null,
    _listeners: [],

    get currentWorkspaceId() {
        return this._currentWorkspaceId;
    },

    set currentWorkspaceId(id) {
        this._currentWorkspaceId = id;
        this._notify();
    },

    addWorkspace(ws) {
        const workspaces = this.getWorkspaces();
        if (!workspaces.find(w => w.workspace_id === ws.workspace_id)) {
            workspaces.push(ws);
            sessionStorage.setItem('workspaces', JSON.stringify(workspaces));
        }
        this._notify();
    },

    getWorkspaces() {
        try {
            return JSON.parse(sessionStorage.getItem('workspaces') || '[]');
        } catch {
            return [];
        }
    },

    onChange(fn) {
        this._listeners.push(fn);
    },

    _notify() {
        this._listeners.forEach(fn => fn());
    },
};