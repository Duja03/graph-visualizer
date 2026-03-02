/**
 * api.js
 * Thin JS client that talks to the Flask explorer API.
 * FLASK_API_URL is injected by Django via base.html.
 */

const API = {
    async getPlugins() {
        const res = await fetch(`${FLASK_API_URL}/api/plugins`);
        return res.json();
    },

    async getPluginParams(pluginId) {
        const res = await fetch(`${FLASK_API_URL}/api/plugins/${pluginId}/params`);
        return res.json();
    },

    async loadGraph(pluginId, params) {
        const res = await fetch(`${FLASK_API_URL}/api/graph/load`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ plugin_id: pluginId, params }),
        });
        return res.json();
    },

    async getGraph(workspaceId) {
        const res = await fetch(`${FLASK_API_URL}/api/graph/${workspaceId}`);
        return res.json();
    },

    async searchGraph(workspaceId, query) {
        const res = await fetch(`${FLASK_API_URL}/api/graph/${workspaceId}/search?q=${encodeURIComponent(query)}`);
        return res.json();
    },

    async filterGraph(workspaceId, filterExpr) {
        const res = await fetch(`${FLASK_API_URL}/api/graph/${workspaceId}/filter`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filter: filterExpr }),
        });
        return res.json();
    },

    async runCli(workspaceId, command) {
        const res = await fetch(`${FLASK_API_URL}/api/graph/${workspaceId}/cli`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command }),
        });
        return res.json();
    },
};