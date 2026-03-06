/**
 * graph.js
 * D3-based rendering for Main View (pan/zoom/drag) and Bird View (minimap).
 * Populated by data fetched from the Flask API via api.js.
 */

let simulation = null;

async function renderGraph(workspaceId) {
    State.currentWorkspaceId = workspaceId;
    const graphData = await API.getGraph(workspaceId);
    drawMainView(graphData);
    drawBirdView(graphData);
}

function drawMainView(graphData) {
    const svg = d3.select('#main-canvas');
    svg.selectAll('*').remove();

    const width = svg.node().clientWidth || 800;
    const height = svg.node().clientHeight || 600;

    // Pan + zoom
    const g = svg.append('g');
    const zoom = d3.zoom().on('zoom', (event) => {
        g.attr('transform', event.transform);
        syncBirdViewport(event.transform, width, height);
    });
    svg.call(zoom);

    // Force simulation
    simulation = d3.forceSimulation(graphData.nodes)
        .force('link', d3.forceLink(graphData.edges).id(d => d.id).distance(80))
        .force('charge', d3.forceManyBody().strength(-200))
        .force('center', d3.forceCenter(width / 2, height / 2));

    // Edges
    const link = g.append('g').selectAll('line')
        .data(graphData.edges)
        .join('line')
        .attr('class', 'edge');

    // Nodes
    const node = g.append('g').selectAll('circle')
        .data(graphData.nodes)
        .join('circle')
        .attr('class', 'node')
        .attr('r', 10)
        .call(d3.drag()
            .on('start', dragStart)
            .on('drag', dragged)
            .on('end', dragEnd))
        .on('mouseover', showNodeDetails)
        .on('click', (event, d) => focusNode(d.id));

    // Labels
    const label = g.append('g').selectAll('text')
        .data(graphData.nodes)
        .join('text')
        .attr('class', 'node-label')
        .text(d => d.label || d.id);

    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
        node.attr('cx', d => d.x).attr('cy', d => d.y);
        label.attr('x', d => d.x + 12).attr('y', d => d.y + 4);
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

function showNodeDetails(event, d) {
    // TODO: show tooltip with node attributes
    console.log('Node details:', d);
}

function focusNode(nodeId) {
    // Highlight node across all three views
    d3.selectAll('.node').classed('focused', d => d.id === nodeId);
    d3.selectAll('.tree-node').classed('focused', d => d.id === nodeId);
    d3.selectAll('.bird-node').classed('focused', d => d.id === nodeId);
}

function dragStart(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x; d.fy = d.y;
}
function dragged(event, d) { d.fx = event.x; d.fy = event.y; }
function dragEnd(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null; d.fy = null;
}

// Search / filter triggers
document.getElementById('btn-search')?.addEventListener('click', async () => {
    const q = document.getElementById('search-input').value;
    if (!State.currentWorkspaceId || !q) return;
    const subgraph = await API.searchGraph(State.currentWorkspaceId, q);
    drawMainView(subgraph);
    drawBirdView(subgraph);
});

document.getElementById('btn-filter')?.addEventListener('click', async () => {
    const expr = document.getElementById('filter-input').value;
    if (!State.currentWorkspaceId || !expr) return;
    const subgraph = await API.filterGraph(State.currentWorkspaceId, expr);
    drawMainView(subgraph);
    drawBirdView(subgraph);
});

document.getElementById('btn-reset')?.addEventListener('click', async () => {
    if (!State.currentWorkspaceId) return;
    const graphData = await API.resetGraph(State.currentWorkspaceId);
    drawMainView(graphData);
    drawBirdView(graphData);
});

const params = new URLSearchParams(window.location.search);
const workspaceId = params.get('workspace');
if (workspaceId) {
    renderGraph(workspaceId);
} else {
    const workspaces = State.getWorkspaces();
    if (workspaces.length > 0) {
        renderGraph(workspaces[workspaces.length - 1].workspace_id);
    }
}