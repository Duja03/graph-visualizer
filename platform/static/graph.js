/**
 * graph.js
 * D3-based rendering for Main View (pan/zoom/drag) and Bird View (minimap).
 * Populated by data fetched from the Flask API via api.js.
 */

async function renderGraph(workspaceId) {
    State.currentWorkspaceId = workspaceId;
    const graphData = await API.getGraph(workspaceId);
    await renderVisualizer(workspaceId);
    // drawBirdView(graphData);
    renderTree(graphData.nodes, graphData.edges);
}

async function renderVisualizer(workspaceId) {
    const html = await API.visualizeGraph(workspaceId);
    const container = document.getElementById('visualizer-container');

    container.innerHTML = '';

    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    doc.querySelectorAll('style').forEach(style => {
        const s = document.createElement('style');
        s.textContent = style.textContent;
        document.head.appendChild(s);
    });

    doc.body.childNodes.forEach(node => {
        if (node.nodeName !== 'SCRIPT' && node.nodeName !== 'STYLE') {
            container.appendChild(document.importNode(node, true));
        }
    });

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

function drawBirdView(graphData) {
    const svg = d3.select('#bird-canvas');
    if (svg.empty()) return;
    svg.selectAll('*').remove();

    const bw = svg.node().clientWidth || 200;
    const bh = svg.node().clientHeight || 150;

    // Scale nodes to fit bird canvas
    const xs = graphData.nodes.map(n => n.x || 0);
    const ys = graphData.nodes.map(n => n.y || 0);
    const xScale = d3.scaleLinear().domain([Math.min(...xs), Math.max(...xs)]).range([5, bw - 5]);
    const yScale = d3.scaleLinear().domain([Math.min(...ys), Math.max(...ys)]).range([5, bh - 5]);

    svg.append('g').selectAll('circle')
        .data(graphData.nodes)
        .join('circle')
        .attr('class', 'bird-node')
        .attr('r', 3)
        .attr('cx', d => xScale(d.x || 0))
        .attr('cy', d => yScale(d.y || 0));

    // Viewport rectangle (synced with main view zoom)
    svg.append('rect')
        .attr('id', 'bird-viewport')
        .attr('class', 'bird-viewport')
        .attr('x', 0).attr('y', 0)
        .attr('width', bw).attr('height', bh);
}

function syncBirdViewport(transform, mainW, mainH) {
    const birdSvg = document.getElementById('bird-canvas');
    if (!birdSvg) return;
    const bw = birdSvg.clientWidth || 200;
    const bh = birdSvg.clientHeight || 150;
    const scaleX = bw / mainW;
    const scaleY = bh / mainH;
    const vw = (mainW / transform.k) * scaleX;
    const vh = (mainH / transform.k) * scaleY;
    const vx = (-transform.x / transform.k) * scaleX;
    const vy = (-transform.y / transform.k) * scaleY;
    d3.select('#bird-viewport')
        .attr('x', vx).attr('y', vy)
        .attr('width', vw).attr('height', vh);
}

// Search / filter triggers
document.getElementById('btn-search')?.addEventListener('click', async () => {
    const q = document.getElementById('search-input').value;
    if (!State.currentWorkspaceId || !q) return;
    const subgraph = await API.searchGraph(State.currentWorkspaceId, q);
    await renderVisualizer(State.currentWorkspaceId);
    drawBirdView(subgraph);
    renderTree(subgraph.nodes, subgraph.edges);
});

document.getElementById('btn-filter')?.addEventListener('click', async () => {
    const expr = document.getElementById('filter-input').value;
    if (!State.currentWorkspaceId || !expr) return;
    const subgraph = await API.filterGraph(State.currentWorkspaceId, expr);
    await renderVisualizer(State.currentWorkspaceId);
    drawBirdView(subgraph);
    renderTree(subgraph.nodes, subgraph.edges);
});

document.getElementById('btn-reset')?.addEventListener('click', async () => {
    if (!State.currentWorkspaceId) return;
    const graphData = await API.resetGraph(State.currentWorkspaceId);
    await renderVisualizer(State.currentWorkspaceId);
    drawBirdView(graphData);
    renderTree(graphData.nodes, graphData.edges);
});

const params = new URLSearchParams(window.location.search);
const workspaceId = params.get('workspace');
if (workspaceId) {
    renderGraph(workspaceId);
} else {
    const lastId = State.currentWorkspaceId;
    if (lastId) renderGraph(lastId);
}