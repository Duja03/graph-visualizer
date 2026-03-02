"""
routes.py — Flask API blueprint.

Endpoints:
  GET  /api/plugins                          → list installed data source plugins
  GET  /api/plugins/<plugin_id>/params       → input params required by a plugin
  POST /api/graph/load                       → load graph via a plugin, returns workspace_id
  GET  /api/graph/<workspace_id>             → full graph (nodes + edges)
  GET  /api/graph/<workspace_id>/search?q=  → search subgraph
  POST /api/graph/<workspace_id>/filter      → filter subgraph
  POST /api/graph/<workspace_id>/cli         → run a CLI command on the graph
"""

from flask import Blueprint, jsonify, request
from .workspace_store import WorkspaceStore
from .plugin_registry import PluginRegistry

api_bp = Blueprint('api', __name__)
store = WorkspaceStore()
registry = PluginRegistry()


@api_bp.route('/plugins', methods=['GET'])
def list_plugins():
    """Return all installed data source plugins."""
    plugins = registry.get_all_plugins()
    return jsonify([
        {'id': p.plugin_id, 'name': p.name, 'description': p.description}
        for p in plugins
    ])


@api_bp.route('/plugins/<plugin_id>/params', methods=['GET'])
def plugin_params(plugin_id):
    """Return the input parameters a plugin requires."""
    plugin = registry.get_plugin(plugin_id)
    if not plugin:
        return jsonify({'error': 'Plugin not found'}), 404
    return jsonify(plugin.get_params())


@api_bp.route('/graph/load', methods=['POST'])
def load_graph():
    """Load a graph using the specified plugin and parameters."""
    data = request.get_json()
    plugin_id = data.get('plugin_id')
    params = data.get('params', {})

    plugin = registry.get_plugin(plugin_id)
    if not plugin:
        return jsonify({'error': f'Plugin "{plugin_id}" not found'}), 404

    try:
        graph = plugin.load(params)
        workspace_id = store.create_workspace(graph, plugin)
        return jsonify({
            'workspace_id': workspace_id,
            'plugin_name': plugin.name,
            'node_count': graph.node_count(),
            'edge_count': graph.edge_count(),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/graph/<workspace_id>', methods=['GET'])
def get_graph(workspace_id):
    """Return the full graph for a workspace as JSON (nodes + edges)."""
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404
    return jsonify(workspace.graph.to_dict())


@api_bp.route('/graph/<workspace_id>/search', methods=['GET'])
def search_graph(workspace_id):
    """Return a subgraph matching the search query."""
    query = request.args.get('q', '')
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404

    from platform.search_engine import SearchEngine  # platform library
    subgraph = SearchEngine.search(workspace.graph, query)
    return jsonify(subgraph.to_dict())


@api_bp.route('/graph/<workspace_id>/filter', methods=['POST'])
def filter_graph(workspace_id):
    """Return a subgraph matching a filter expression (e.g. 'Age > 30')."""
    data = request.get_json()
    filter_expr = data.get('filter', '')
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404

    from platform.filter_engine import FilterEngine  # platform library
    try:
        subgraph = FilterEngine.filter(workspace.graph, filter_expr)
        return jsonify(subgraph.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/graph/<workspace_id>/cli', methods=['POST'])
def run_cli(workspace_id):
    """Execute a CLI command against the graph."""
    data = request.get_json()
    command = data.get('command', '')
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404

    from platform.cli_engine import CLIEngine  # platform library
    try:
        result = CLIEngine.run(workspace.graph, command)
        return jsonify({'message': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400