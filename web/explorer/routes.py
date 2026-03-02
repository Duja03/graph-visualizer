"""
routes.py — Flask API blueprint.
"""

from flask import Blueprint, jsonify, request
from .workspace_store import WorkspaceStore
from .plugin_registry import PluginRegistry

api_bp = Blueprint('api', __name__)
store = WorkspaceStore()
registry = PluginRegistry()


def serialize_graph(graph):
    """
    Serialize a Graph instance to a JSON-safe dict.
    Graph has no to_dict() so we build it manually.
    Handles date objects which are not JSON serialisable by default.
    """
    from datetime import date

    def serialize_value(v):
        if isinstance(v, date):
            return v.isoformat()
        return v

    nodes = [
        {
            'id': node.id,
            'label': node.attributes.get('name') or node.attributes.get('label') or node.id,
            'attributes': {k: serialize_value(v) for k, v in node.attributes.items()},
        }
        for node in graph.nodes.values()
    ]

    edges = [
        {
            'id': edge.id,
            'source': edge.source,
            'target': edge.target,
            'attributes': {k: serialize_value(v) for k, v in edge.attributes.items()},
        }
        for edge in graph.edges.values()
    ]

    return {'directed': graph.directed, 'nodes': nodes, 'edges': edges}


@api_bp.route('/plugins', methods=['GET'])
def list_plugins():
    plugins = registry.get_all_plugins()
    return jsonify([
        {
            'id': p.static_identifier,
            'name': p.static_identifier,
            'description': getattr(p, 'description', ''),
        }
        for p in plugins
    ])


@api_bp.route('/plugins/<plugin_id>/params', methods=['GET'])
def plugin_params(plugin_id):
    plugin_cls = registry.get_plugin(plugin_id)
    if not plugin_cls:
        return jsonify({'error': 'Plugin not found'}), 404
    return jsonify([
        {'name': 'filepath', 'label': 'File path', 'placeholder': '/path/to/file'}
    ])


@api_bp.route('/graph/load', methods=['POST'])
def load_graph():
    data = request.get_json()
    plugin_id = data.get('plugin_id')
    params = data.get('params', {})

    plugin_cls = registry.get_plugin(plugin_id)
    if not plugin_cls:
        return jsonify({'error': f'Plugin "{plugin_id}" not found'}), 404

    try:
        plugin_instance = plugin_cls()
        graph = plugin_instance.load(params.get('filepath', ''))
        workspace_id = store.create_workspace(graph, plugin_instance)
        return jsonify({
            'workspace_id': workspace_id,
            'plugin_name': plugin_id,
            'node_count': graph.node_count(),
            'edge_count': graph.edge_count(),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/graph/<workspace_id>', methods=['GET'])
def get_graph(workspace_id):
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404
    return jsonify(serialize_graph(workspace.graph))


@api_bp.route('/graph/<workspace_id>/search', methods=['GET'])
def search_graph(workspace_id):
    query = request.args.get('q', '')
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404

    from platform.src.core.search_engine import SearchEngine
    try:
        subgraph = SearchEngine(workspace.graph).search(query)
        return jsonify(serialize_graph(subgraph))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/graph/<workspace_id>/filter', methods=['POST'])
def filter_graph(workspace_id):
    data = request.get_json()
    filter_expr = data.get('filter', '')
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404

    from platform.src.core.filter_engine import FilterEngine
    try:
        subgraph = FilterEngine.apply(workspace.graph, filter_expr)
        return jsonify(serialize_graph(subgraph))
    except ValueError as e:
        # FilterError subclasses ValueError so this catches both
        return jsonify({'error': str(e)}), 400


@api_bp.route('/graph/<workspace_id>/cli', methods=['POST'])
def run_cli(workspace_id):
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404

    # Stub — replace once CLIEngine is implemented in platform
    # from platform.src.core.cli_engine import CLIEngine
    return jsonify({'error': 'CLI engine not yet implemented'}), 501