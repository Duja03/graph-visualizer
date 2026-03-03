// api.js — calls Django's own API endpoints, no Flask dependency

const API = {
    async getPlugins() {
        const res = await fetch(`/api/plugins`);
        return res.json();
    },
    async getPluginParams(pluginId) {
        const res = await fetch(`/api/plugins/${pluginId}/params`);
        return res.json();
    },
    async loadGraph(pluginId, params) {
        const res = await fetch(`/api/graph/load`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ plugin_id: pluginId, params }),
        });
        return res.json();
    },
    async getGraph(workspaceId) {
        const res = await fetch(`/api/graph/${workspaceId}`);
        return res.json();
    },
    async searchGraph(workspaceId, query) {
        const res = await fetch(`/api/graph/${workspaceId}/search?q=${encodeURIComponent(query)}`);
        return res.json();
    },
    async filterGraph(workspaceId, filterExpr) {
        const res = await fetch(`/api/graph/${workspaceId}/filter`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filter: filterExpr }),
        });
        return res.json();
    },
};