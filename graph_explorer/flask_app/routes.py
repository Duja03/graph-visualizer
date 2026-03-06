"""
routes.py — Flask web application routes.
Serves frontend templates and API endpoints.
Talks directly to platform and plugins — no Django dependency.
"""

from flask import Blueprint, jsonify, request, render_template
from core.workspace_store import WorkspaceStore
from core.plugin_registry import PluginRegistry
from core.search_engine import SearchEngine
from core.filter_engine import FilterEngine

api_bp = Blueprint('api', __name__)
store = WorkspaceStore()
registry = PluginRegistry()


def serialize_graph(graph):
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


# Template views 

@api_bp.route('/')
def main_view():
    return render_template('main.html', active_view='main')

@api_bp.route('/tree/')
def tree_view():
    return render_template('tree-view.html', active_view='tree')

@api_bp.route('/map/')
def map_view():
    return render_template('map-view.html', active_view='map')

@api_bp.route('/workspace/')
def workspace_view():
    return render_template('workspace.html', active_view='workspace')


# API endpoints 

@api_bp.route('/api/plugins', methods=['GET'])
def list_plugins():
    plugins = registry.get_all_plugins()
    return jsonify([
        {
            'id': p().plugin_id(),
            'name': p().name(),
            'description': getattr(p(), 'description', ''),
        }
        for p in plugins
    ])


@api_bp.route('/api/plugins/<plugin_id>/params', methods=['GET'])
def plugin_params(plugin_id):
    plugin_cls = registry.get_plugin(plugin_id)
    if not plugin_cls:
        return jsonify({'error': 'Plugin not found'}), 404
    plugin = plugin_cls()
    params = [
        {
            'name': param_name,
            'label': param_desc,
            'placeholder': param_desc,
        }
        for param_name, param_desc in plugin.parameters().items()
    ]
    return jsonify(params)


@api_bp.route('/api/graph/load', methods=['POST'])
def load_graph():
    data = request.get_json()
    plugin_id = data.get('plugin_id')
    params = data.get('params', {})

    plugin_cls = registry.get_plugin(plugin_id)
    if not plugin_cls:
        return jsonify({'error': f'Plugin "{plugin_id}" not found'}), 404

    try:
        plugin_instance = plugin_cls()
        graph = plugin_instance.load(**params)
        workspace_id = store.create_workspace(graph, plugin_instance)
        return jsonify({
            'workspace_id': workspace_id,
            'plugin_name': plugin_id,
            'node_count': graph.node_count(),
            'edge_count': graph.edge_count(),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/api/graph/<workspace_id>', methods=['GET'])
def get_graph(workspace_id):
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404
    return jsonify(serialize_graph(workspace.graph))


@api_bp.route('/api/graph/<workspace_id>/search', methods=['GET'])
def search_graph(workspace_id):
    query = request.args.get('q', '')
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404
    try:
        subgraph = SearchEngine(workspace.graph).search(query)
        workspace.graph = subgraph
        return jsonify(serialize_graph(subgraph))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/api/graph/<workspace_id>/filter', methods=['POST'])
def filter_graph(workspace_id):
    data = request.get_json()
    filter_expr = data.get('filter', '')
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404
    try:
        subgraph = FilterEngine.filter(workspace.graph, filter_expr)
        workspace.graph = subgraph
        return jsonify(serialize_graph(subgraph))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/api/graph/<workspace_id>/cli', methods=['POST'])
def run_cli(workspace_id):
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404
    return jsonify({'error': 'CLI engine not yet implemented'}), 501

@api_bp.route('/api/graph/<workspace_id>/reset', methods=['POST'])
def reset_graph(workspace_id):
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404
    workspace.graph = workspace.initial_graph
    return jsonify(serialize_graph(workspace.initial_graph))