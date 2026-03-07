/**
 * tree.js
 * Renders a collapsible package-explorer-style tree view.
 * Each node can be expanded (+) or collapsed (−).
 */

// Inject the .selected style for tree nodes once
(function injectTreeSelectedStyle() {
    if (document.getElementById('tree-selected-style')) return;
    const s = document.createElement('style');
    s.id = 'tree-selected-style';
    s.textContent = `
        .tree-node-header.selected {
            background: var(--violet-600) !important;
            border-radius: 999px;
        }
        .tree-node-header.selected .tree-label,
        .tree-node-header.selected .tree-toggle,
        .tree-node-header.selected .tree-leaf-marker {
            color: white !important;
        }
    `;
    document.head.appendChild(s);
})();

function getRootNodes(nodes, edges) {
    const hasParent = new Set(edges.map(e => getEdgeId(e.target)));
    return nodes.filter(n => !hasParent.has(n.id));
}

function getEdgeId(endpoint) {
    // After D3 simulation: endpoint is a full object { id, x, y, ... }
    // From raw API response: endpoint is a string
    return typeof endpoint === 'object' ? endpoint.id : endpoint;
}

function renderTree(nodes, edges) {
    const container = document.getElementById('tree-container');
    if (!container) return;
    container.innerHTML = '';

    const nodeMap = Object.fromEntries(nodes.map(n => [n.id, n]));
    const childrenMap = Object.fromEntries(nodes.map(n => [n.id, []]));

    edges.forEach(edge => {
        const sourceId = getEdgeId(edge.source);
        const targetId = getEdgeId(edge.target);
        if (childrenMap[sourceId] !== undefined) childrenMap[sourceId].push(targetId);
    });

    const roots = getRootNodes(nodes, edges);
    const topLevel = roots.length ? roots : [nodes[0]];

    topLevel.forEach(root => {
        container.appendChild(buildTreeNode(root, childrenMap, nodeMap, new Set()));
    });
}

function buildTreeNode(node, childrenMap, nodeMap, visited) {
    const childIds = childrenMap[node.id] || [];
    const hasChildren = childIds.length > 0;
    const isCycle = visited.has(node.id);

    const item = document.createElement('div');
    item.className = 'tree-node';
    item.dataset.id = node.id;

    const wrapper = document.createElement('div');
    wrapper.className = 'tree-node-wrapper';

    const header = document.createElement('div');
    header.className = 'tree-node-header';

    if (hasChildren && !isCycle) {
        const toggle = document.createElement('span');
        toggle.className = 'tree-toggle expanded';
        toggle.textContent = '−';
        header.appendChild(toggle);
    } else if (isCycle) {
        const cycleMarker = document.createElement('span');
        cycleMarker.className = 'tree-cycle-marker';
        cycleMarker.textContent = '↺';
        cycleMarker.title = 'Cycle detected';
        header.appendChild(cycleMarker);
    } else {
        const leaf = document.createElement('span');
        leaf.className = 'tree-leaf-marker';
        leaf.textContent = '·';
        header.appendChild(leaf);
    }

    const label = document.createElement('span');
    label.className = 'tree-label';
    label.textContent = node.label || node.id;
    label.onclick = (e) => {
        e.stopPropagation();
        window.focusNode(node.id);
    };
    header.appendChild(label);

    const attrs = node.attributes || {};
    const attrEntries = Object.entries(attrs);
    if (attrEntries.length > 0) {
        const attrToggle = document.createElement('span');
        attrToggle.className = 'tree-attr-toggle';
        attrToggle.textContent = '{}';
        attrToggle.title = 'Show attributes';
        header.appendChild(attrToggle);

        const attrPanel = document.createElement('div');
        attrPanel.className = 'tree-attr-panel';
        attrPanel.style.display = 'none';
        attrEntries.forEach(([key, val]) => {
            const row = document.createElement('div');
            row.className = 'tree-attr-row';
            row.innerHTML = `<span class="tree-attr-key">${key}</span><span class="tree-attr-val">${val}</span>`;
            attrPanel.appendChild(row);
        });

        attrToggle.addEventListener('click', function (e) {
            e.stopPropagation();
            const isOpen = attrPanel.style.display !== 'none';
            attrPanel.style.display = isOpen ? 'none' : 'block';
            attrToggle.classList.toggle('active', !isOpen);
        });

        wrapper.appendChild(header);
        wrapper.appendChild(attrPanel); // ← attrPanel inside wrapper, after header
    } else {
        wrapper.appendChild(header);
    }

    item.appendChild(wrapper); // ← wrapper first

    if (hasChildren && !isCycle) {
        const childContainer = document.createElement('div');
        childContainer.className = 'tree-children';

        const newVisited = new Set(visited);
        newVisited.add(node.id);

        childIds.forEach(childId => {
            const childNode = nodeMap[childId];
            if (childNode) childContainer.appendChild(buildTreeNode(childNode, childrenMap, nodeMap, newVisited));
        });

        header.querySelector('.tree-toggle').addEventListener('click', function () {
            const isExpanded = this.textContent === '−';
            this.textContent = isExpanded ? '+' : '−';
            this.classList.toggle('expanded', !isExpanded);
            childContainer.style.display = isExpanded ? 'none' : 'block';
        });

        item.appendChild(childContainer); // ← childContainer after wrapper
    }

    return item;
}