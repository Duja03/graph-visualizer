/**
 * graph.js
 * D3-based rendering for Main View (pan/zoom/drag) and Bird View (minimap).
 * Populated by data fetched from the Flask API via api.js.
 */

async function renderGraph(workspaceId) {
    State.currentWorkspaceId = workspaceId;
    const graphData = await API.getGraph(workspaceId);
    await renderVisualizer(workspaceId);
    renderTree(graphData.nodes, graphData.edges);
}

async function renderVisualizer(workspaceId) {
    const html = await API.visualizeGraph(workspaceId);
    const container = document.getElementById('visualizer-container');
    container.innerHTML = '';

    const birdCanvas = document.getElementById('bird-canvas');
    if (birdCanvas) birdCanvas.querySelectorAll('g').forEach(g => g.remove())

    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    // Inject styles into document head
    doc.querySelectorAll('style').forEach(style => {
        const s = document.createElement('style');
        s.textContent = style.textContent;
        document.head.appendChild(s);
    });

    // Inject DOM elements (skip scripts and styles)
    doc.body.childNodes.forEach(node => {
        if (node.nodeName !== 'SCRIPT' && node.nodeName !== 'STYLE') {
            container.appendChild(document.importNode(node, true));
        }
    });

    // Inject scripts — skip duplicate external src
    doc.querySelectorAll('script').forEach(oldScript => {
        const s = document.createElement('script');
        if (oldScript.src) {
            if (document.querySelector(`script[src="${oldScript.src}"]`)) return;
            s.src = oldScript.src;
        } else {
            s.textContent = oldScript.textContent;
        }
        document.body.appendChild(s);
    });
}

// Search / filter triggers
document.getElementById('btn-search')?.addEventListener('click', async () => {
    const q = document.getElementById('search-input').value;
    if (!State.currentWorkspaceId || !q) return;
    const subgraph = await API.searchGraph(State.currentWorkspaceId, q);
    if (subgraph.error) { alert('Search error: ' + subgraph.error); return; }
    await renderVisualizer(State.currentWorkspaceId);
    renderTree(subgraph.nodes, subgraph.edges);
});

document.getElementById('btn-filter')?.addEventListener('click', async () => {
    const expr = document.getElementById('filter-input').value;
    if (!State.currentWorkspaceId || !expr) return;
    const subgraph = await API.filterGraph(State.currentWorkspaceId, expr);
    if (subgraph.error) { alert('Filter error: ' + subgraph.error); return; }
    await renderVisualizer(State.currentWorkspaceId);
    renderTree(subgraph.nodes, subgraph.edges);
});

document.getElementById('btn-reset')?.addEventListener('click', async () => {
    if (!State.currentWorkspaceId) return;
    const graphData = await API.resetGraph(State.currentWorkspaceId);
    if (graphData.error) { alert('Reset error: ' + graphData.error); return; }
    await renderVisualizer(State.currentWorkspaceId);
    renderTree(graphData.nodes, graphData.edges);
});

// ─── Auto-load from URL param ───

const params = new URLSearchParams(window.location.search);
const workspaceId = params.get('workspace');
if (workspaceId) {
    renderGraph(workspaceId);
} else {
    const lastId = State.currentWorkspaceId;
    if (lastId) renderGraph(lastId);
}

// ── Global selection state ───────────────────────────────────────────────────

let selectedNodeId = null;

function focusNode(nodeOrId) {
    const nodeId = (typeof nodeOrId === 'object') ? nodeOrId.id : nodeOrId;
    if (!nodeId) return;

    selectedNodeId = nodeId;

    window.dispatchEvent(new CustomEvent('graph:focusNode', { detail: { nodeId } }));

    _focusTreeNode(nodeId);
}

// Expose globally so visualizer templates and tree.js can call it
window.focusNode = focusNode;

function _focusTreeNode(nodeId) {
    // Remove previous highlight
    document.querySelectorAll('.tree-node-header.selected').forEach(el => {
        el.classList.remove('selected');
    });

    const treeEl = document.querySelector(`.tree-node[data-id="${CSS.escape(nodeId)}"]`);
    if (!treeEl) return;

    const header = treeEl.querySelector('.tree-node-header');
    if (header) {
        header.classList.add('selected');
        header.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}