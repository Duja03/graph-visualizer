/**
 * graph.js
 * D3-based rendering for Main View (pan/zoom/drag) and Bird View (minimap).
 * Populated by data fetched from the Flask API via api.js.
 */

async function renderGraph(workspaceId) {
    State.currentWorkspaceId = workspaceId;
    const graphData = await API.getGraph(workspaceId);
    if (graphData.error) {
        showExpiredModal();
        return;
    }

    await renderVisualizer(workspaceId);
    renderTree(graphData.nodes, graphData.edges);
}

function showExpiredModal() {
    const modal = document.createElement('div');
    modal.innerHTML = `
        <div id="expired-overlay" style="
            position: fixed; inset: 0; z-index: 1000;
            background: rgba(109,40,217,0.18);
            backdrop-filter: blur(4px);
            display: flex; align-items: center; justify-content: center;">
            <div style="
                background: white; border-radius: 14px;
                padding: 2rem 2.5rem; max-width: 380px; width: 90%;
                box-shadow: 0 8px 40px rgba(109,40,217,0.22);
                text-align: center;">
                <span class="material-icons" style="font-size:2.5rem;color:var(--violet-600);">cloud_off</span>
                <h2 style="margin:0.75rem 0 0.5rem;color:var(--violet-700);font-size:1.2rem;">Workspace Expired</h2>
                <p style="color:var(--gray-500);font-size:0.92rem;margin-bottom:1.5rem;">
                    This workspace is no longer available. Please load your data again.
                </p>
                <button id="expired-btn" style="
                    background: var(--violet-600); color: white;
                    border: none; border-radius: 8px;
                    padding: 0.6rem 1.8rem; font-size: 0.95rem;
                    cursor: pointer;">
                    Go to Workspace
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    document.getElementById('expired-btn').addEventListener('click', () => {
        sessionStorage.clear();
        window.location.href = '/workspace/';
    });
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