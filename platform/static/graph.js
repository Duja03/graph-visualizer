/**
 * graph.js
 * D3-based rendering for Main View (pan/zoom/drag) and Bird View (minimap).
 * Populated by data fetched from the Flask API via api.js.
 */

// ── Bird View internal state ─────────────────────────────────────────────────
let _birdNodes      = [];   // [{id, x, y}] in bird-canvas coordinate space
let _birdXScale     = null;
let _birdYScale     = null;
let _lastTransform  = { x: 0, y: 0, k: 1 };
let _lastMainW      = 800;
let _lastMainH      = 600;
let _birdReady      = false;

async function renderGraph(workspaceId) {
    State.currentWorkspaceId = workspaceId;
    const graphData = await API.getGraph(workspaceId);
    await renderVisualizer(workspaceId);
    renderTree(graphData.nodes, graphData.edges);
    // Bird view will self-initialize once it receives "visualizer:positions"
    // But also do an eager draw with API data if available
    _birdEagerDraw(graphData.nodes);
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

/**
 * Do an initial bird-view draw using node list from the API response.
 * Positions are unknown at this point so we run a quick D3 force layout.
 */
function _birdEagerDraw(apiNodes) {
    if (!apiNodes || apiNodes.length === 0) return;

    const svgEl = document.getElementById('bird-canvas');
    if (!svgEl) return;

    const bw = svgEl.clientWidth  || svgEl.getBoundingClientRect().width  || 220;
    const bh = svgEl.clientHeight || svgEl.getBoundingClientRect().height || 160;

    if (bw < 10 || bh < 10) return;   // panel not yet laid out

    // Use whatever node positions are already available (may all be 0,0 at start)
    const xs = apiNodes.map(n => n.x || 0);
    const ys = apiNodes.map(n => n.y || 0);
    _updateBirdScales(xs, ys, bw, bh);

    _birdNodes = apiNodes.map(n => ({
        id: n.id,
        bx: _birdXScale(n.x || 0),
        by: _birdYScale(n.y || 0),
    }));

    _redrawBirdCanvas(bw, bh);
}

/**
 * Called when the main simulation broadcasts settled node positions.
 * This gives us the "true" layout coordinates.
 */
function _birdOnPositions(nodes) {
    const svgEl = document.getElementById('bird-canvas');
    if (!svgEl) return;

    const bw = svgEl.clientWidth  || svgEl.getBoundingClientRect().width  || 220;
    const bh = svgEl.clientHeight || svgEl.getBoundingClientRect().height || 160;
    if (bw < 10 || bh < 10) return;

    const xs = nodes.map(n => n.x || 0);
    const ys = nodes.map(n => n.y || 0);
    _updateBirdScales(xs, ys, bw, bh);

    _birdNodes = nodes.map(n => ({
        id: n.id,
        bx: _birdXScale(n.x),
        by: _birdYScale(n.y),
    }));

    _birdReady = true;
    _redrawBirdCanvas(bw, bh);
    // Restore last known viewport rect
    _syncBirdViewport(_lastTransform, _lastMainW, _lastMainH);
}

/**
 * Build linear scales that map main-sim coordinates → bird canvas pixels.
 */
function _updateBirdScales(xs, ys, bw, bh) {
    const PAD = 10;
    let xMin = Math.min(...xs), xMax = Math.max(...xs);
    let yMin = Math.min(...ys), yMax = Math.max(...ys);

    // Avoid degenerate (single point) graphs
    if (xMin === xMax) { xMin -= 1; xMax += 1; }
    if (yMin === yMax) { yMin -= 1; yMax += 1; }

    _birdXScale = function(v) { return PAD + (v - xMin) / (xMax - xMin) * (bw - 2 * PAD); };
    _birdYScale = function(v) { return PAD + (v - yMin) / (yMax - yMin) * (bh - 2 * PAD); };

    // Store inverse for viewport maths
    _birdXScale.invert = function(bx) { return xMin + (bx - PAD) / (bw - 2 * PAD) * (xMax - xMin); };
    _birdYScale.invert = function(by) { return yMin + (by - PAD) / (bh - 2 * PAD) * (yMax - yMin); };

    _birdXScale._domain = [xMin, xMax];
    _birdYScale._domain = [yMin, yMax];
    _birdXScale._range  = [PAD, bw - PAD];
    _birdYScale._range  = [PAD, bh - PAD];
}

/**
 * Redraw the bird canvas: clear, draw edges (if available), draw node dots,
 * then redraw viewport rect on top.
 */
function _redrawBirdCanvas(bw, bh) {
    const svg = d3.select('#bird-canvas');
    if (svg.empty()) return;

    // Keep viewport rect element — remove everything else
    svg.selectAll('.bird-inner').remove();
    const g = svg.append('g').attr('class', 'bird-inner');

    // Node dots
    g.selectAll('.bird-node')
        .data(_birdNodes)
        .enter().append('circle')
        .attr('class', 'bird-node')
        .attr('r', Math.max(2, Math.min(4, 200 / Math.max(_birdNodes.length, 1))))
        .attr('cx', function(d) { return d.bx; })
        .attr('cy', function(d) { return d.by; })
        .attr('fill', 'var(--violet-500)')
        .attr('opacity', 0.8);

    // Make sure viewport rect stays on top
    const vp = document.getElementById('bird-viewport');
    if (vp) svg.node().appendChild(vp);
}


/**
 * Update the viewport rectangle position/size based on main view transform.
 *
 * The main view canvas has width mainW, height mainH.
 * The D3 zoom transform is { x, y, k }.
 *
 * A point at (px, py) in main-sim space maps to screen as:
 *   screen_x = px * k + x
 *   screen_y = py * k + y
 *
 * The visible region in sim space is therefore:
 *   sim_left   = (0    - x) / k
 *   sim_top    = (0    - y) / k
 *   sim_right  = (mainW - x) / k
 *   sim_bottom = (mainH - y) / k
 *
 * We then map those sim coords → bird canvas pixels using _birdXScale/_birdYScale.
 */
function _syncBirdViewport(transform, mainW, mainH) {
    const vp = d3.select('#bird-viewport');
    if (vp.empty() || !_birdXScale || !_birdYScale) return;

    const svgEl = document.getElementById('bird-canvas');
    if (!svgEl) return;

    const bw = svgEl.clientWidth  || svgEl.getBoundingClientRect().width  || 220;
    const bh = svgEl.clientHeight || svgEl.getBoundingClientRect().height || 160;

    const { x, y, k } = transform;

    // Sim-space extents of the main viewport
    const simLeft   = (0     - x) / k;
    const simTop    = (0     - y) / k;
    const simRight  = (mainW - x) / k;
    const simBottom = (mainH - y) / k;

    // Bird-canvas pixel coords
    const bx1 = _birdXScale(simLeft);
    const by1 = _birdYScale(simTop);
    const bx2 = _birdXScale(simRight);
    const by2 = _birdYScale(simBottom);

    vp.attr('x',      bx1)
      .attr('y',      by1)
      .attr('width',  Math.abs(bx2 - bx1))
      .attr('height', Math.abs(by2 - by1));
}


// ── Event listeners from visualizer plugin ───────────────────────────────────

// Throttle bird-view redraws to max ~30fps (every 33ms) to avoid
// re-drawing on every D3 simulation tick (which fires ~60x/s)
var _birdPositionTimer = null;
window.addEventListener('visualizer:positions', function(e) {
    if (_birdPositionTimer) return;
    _birdPositionTimer = setTimeout(function() {
        _birdPositionTimer = null;
        _birdOnPositions(e.detail.nodes);
    }, 33);
});

window.addEventListener('visualizer:zoom', function(e) {
    const { transform, mainW, mainH } = e.detail;
    _lastTransform = transform;
    _lastMainW     = mainW  || _lastMainW;
    _lastMainH     = mainH  || _lastMainH;
    if (_birdReady) {
        _syncBirdViewport(transform, _lastMainW, _lastMainH);
    }
});

// Search / filter triggers
document.getElementById('btn-search')?.addEventListener('click', async () => {
    const q = document.getElementById('search-input').value;
    if (!State.currentWorkspaceId || !q) return;
    const subgraph = await API.searchGraph(State.currentWorkspaceId, q);
    if (subgraph.error) { alert('Search error: ' + subgraph.error); return; }
    await renderVisualizer(State.currentWorkspaceId);
    _birdEagerDraw(subgraph.nodes);
    renderTree(subgraph.nodes, subgraph.edges);
});

document.getElementById('btn-filter')?.addEventListener('click', async () => {
    const expr = document.getElementById('filter-input').value;
    if (!State.currentWorkspaceId || !expr) return;
    const subgraph = await API.filterGraph(State.currentWorkspaceId, expr);
    if (subgraph.error) { alert('Filter error: ' + subgraph.error); return; }
    await renderVisualizer(State.currentWorkspaceId);
    _birdEagerDraw(subgraph.nodes);
    renderTree(subgraph.nodes, subgraph.edges);
});

document.getElementById('btn-reset')?.addEventListener('click', async () => {
    if (!State.currentWorkspaceId) return;
    const graphData = await API.resetGraph(State.currentWorkspaceId);
    if (graphData.error) { alert('Reset error: ' + graphData.error); return; }
    await renderVisualizer(State.currentWorkspaceId);
    _birdEagerDraw(graphData.nodes);
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