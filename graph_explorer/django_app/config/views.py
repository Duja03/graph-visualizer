"""
Django views — renders templates AND exposes API endpoints
that talk directly to platform (no Flask dependency).
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
import json

from core.workspace_store import WorkspaceStore
from core.plugin_registry import PluginRegistry

store = WorkspaceStore()
registry = PluginRegistry()

# Template views 

def main_view(request):
    return render(request, 'main.html', {'active_view': 'main'})

def tree_view(request):
    return render(request, 'tree-view.html', {'active_view': 'tree'})

def map_view(request):
    return render(request, 'map-view.html', {'active_view': 'map'})

def workspace_view(request):
    return render(request, 'workspace.html', {'active_view': 'workspace'})

# API endpoints 

def api_datasource_plugins(request):
    plugins = registry.get_all_datasource_plugins()
    return JsonResponse([
        {
            'id': p().plugin_id(),
            'name': p().name(),
            'description': getattr(p(), 'description', ''),
        }
        for p in plugins
    ], safe=False)

def api_visualizer_plugins(request):
    plugins = registry.get_all_visualizer_plugins()
    return JsonResponse([
        {
            'id': p().plugin_id(),
            'name': p().name(),
            'description': getattr(p(), 'description', ''),
        }
        for p in plugins
    ], safe=False)

def api_plugin_params(request, plugin_id):
    plugin_cls = registry.get_plugin(plugin_id)
    if not plugin_cls:
        return JsonResponse({'error': 'Plugin not found'}, status=404)
    plugin = plugin_cls()
    params = [
        {
            'name': param_name,
            'label': param_desc,
            'placeholder': param_desc,
        }
        for param_name, param_desc in plugin.parameters().items()
    ]
    return JsonResponse(params, safe=False)


@csrf_exempt
def api_load_graph(request):
    data = json.loads(request.body)
    plugin_id = data.get('plugin_id')
    params = data.get('params', {})

    plugin_cls = registry.get_plugin(plugin_id)
    if not plugin_cls:
        return JsonResponse({'error': f'Plugin "{plugin_id}" not found'}, status=404)

    try:
        plugin_instance = plugin_cls()
        graph = plugin_instance.load(**params)
        workspace_id = store.create_workspace(graph, plugin_instance)
        return JsonResponse({
            'workspace_id': workspace_id,
            'plugin_name': plugin_id,
            'node_count': graph.node_count(),
            'edge_count': graph.edge_count(),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def api_get_graph(request, workspace_id):
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return JsonResponse({'error': 'Workspace not found'}, status=404)
    return JsonResponse(serialize_graph(workspace.graph))


def api_search_graph(request, workspace_id):
    query = request.GET.get('q', '')
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return JsonResponse({'error': 'Workspace not found'}, status=404)
    from core.search_engine import SearchEngine
    try:
        subgraph = SearchEngine(workspace.graph).search(query)
        workspace.graph = subgraph
        return JsonResponse(serialize_graph(subgraph))
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_filter_graph(request, workspace_id):
    data = json.loads(request.body)
    filter_expr = data.get('filter', '')
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return JsonResponse({'error': 'Workspace not found'}, status=404)
    from core.filter_engine import FilterEngine
    try:
        subgraph = FilterEngine.filter(workspace.graph, filter_expr)
        workspace.graph = subgraph
        return JsonResponse(serialize_graph(subgraph))
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def api_reset_graph(request, workspace_id):
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return JsonResponse({'error': 'Workspace not found'}, status=404)
    workspace.graph = workspace.initial_graph
    return JsonResponse(serialize_graph(workspace.initial_graph))

def serialize_graph(graph):
    from datetime import date
    def serialize_value(v):
        return v.isoformat() if isinstance(v, date) else v

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