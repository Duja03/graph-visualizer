/**
 * tree.js
 * Renders a collapsible package-explorer-style tree view.
 * Each node can be expanded (+) or collapsed (−).
 */

function renderTree(nodes, rootId) {
    const container = document.getElementById('tree-container');
    if (!container) return;
    container.innerHTML = '';

    // Build adjacency map
    const childrenMap = {};
    nodes.forEach(n => { childrenMap[n.id] = n.children || []; });

    const root = nodes.find(n => n.id === rootId) || nodes[0];
    if (!root) return;

    container.appendChild(buildTreeNode(root, childrenMap, new Set()));
}

function buildTreeNode(node, childrenMap, visited) {
    const children = childrenMap[node.id] || [];
    const hasChildren = children.length > 0;
    const isCycle = visited.has(node.id);

    const item = document.createElement('div');
    item.className = 'tree-node';
    item.dataset.id = node.id;

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
    label.onclick = () => focusNode(node.id);
    header.appendChild(label);

    item.appendChild(header);

    if (hasChildren && !isCycle) {
        const childContainer = document.createElement('div');
        childContainer.className = 'tree-children';

        const newVisited = new Set(visited);
        newVisited.add(node.id);

        children.forEach(childId => {
            const childNode = { id: childId, label: childId, children: childrenMap[childId] || [] };
            childContainer.appendChild(buildTreeNode(childNode, childrenMap, newVisited));
        });

        // Toggle expand/collapse
        header.querySelector('.tree-toggle').addEventListener('click', function () {
            const isExpanded = this.textContent === '−';
            this.textContent = isExpanded ? '+' : '−';
            this.classList.toggle('expanded', !isExpanded);
            childContainer.style.display = isExpanded ? 'none' : 'block';
        });

        item.appendChild(childContainer);
    }

    return item;
}