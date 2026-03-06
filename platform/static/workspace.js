/**
 * workspace.js
 * Loads available plugins and manages workspace creation.
 */

async function initWorkspacePage() {
    const plugins = await API.getDataSourcePlugins();
    const selector = document.getElementById('plugin-selector');
    if (plugins.length === 0) {
        selector.innerHTML = '<option value="">No plugins found :(</option>';
    }
    plugins.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = p.name;
        selector.appendChild(opt);
    });

    // re-render list if State already has workspaces (e.g. back navigation)
    renderWorkspaceList();
}

document.getElementById('plugin-selector')?.addEventListener('change', async function () {
    const pluginId = this.value;
    if (!pluginId) return;
    const params = await API.getPluginParams(pluginId);
    if (!Array.isArray(params)) {
        console.error('Failed to load plugin params:', params);
        document.getElementById('plugin-params').innerHTML =
            '<p style="color:red;font-size:0.85rem;">Could not load plugin parameters.</p>';
        return;
    }
    renderPluginParams(params);
});

function renderPluginParams(params) {
    const container = document.getElementById('plugin-params');
    container.innerHTML = '';
    params.forEach(param => {
        const label = document.createElement('label');
        label.textContent = param.label;
        const input = document.createElement('input');
        input.type = 'text';
        input.name = param.name;
        input.placeholder = param.placeholder || '';
        input.className = 'toolbar-input';
        container.appendChild(label);
        container.appendChild(input);
    });
}

document.getElementById('btn-load')?.addEventListener('click', async () => {
    const pluginId = document.getElementById('plugin-selector').value;
    if (!pluginId) return;

    const paramInputs = document.querySelectorAll('#plugin-params input');
    const params = {};
    paramInputs.forEach(inp => { params[inp.name] = inp.value; });

    const result = await API.loadGraph(pluginId, params);
    if (result.workspace_id) {
        State.addWorkspace(result);
        renderWorkspaceList();
    }
});

function renderWorkspaceList() {
    const container = document.getElementById('workspace-list-container');
    container.innerHTML = '';
    const workspaces = State.getWorkspaces();
    if (workspaces.length === 0) {
        container.innerHTML = '<p class="empty-state">No workspaces loaded yet.</p>';
        return;
    }
    workspaces.forEach(ws => {
        const item = document.createElement('div');
        item.className = 'workspace-item';
        item.innerHTML = `
            <strong>${ws.plugin_name}</strong> — ${ws.node_count} nodes, ${ws.edge_count} edges
            <a href="/?workspace=${ws.workspace_id}" class="btn btn-sm">Open</a>
        `;
        container.appendChild(item);
    });
}

initWorkspacePage();