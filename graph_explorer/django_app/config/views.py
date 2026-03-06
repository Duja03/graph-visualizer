"""
Django views — renders templates AND exposes API endpoints
that talk directly to platform (no Flask dependency).
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from core import Platform
from core.plugin_registry import PluginRegistry

platform = Platform()
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
        workspace_id = platform.create_workspace(graph, plugin_instance)
        return JsonResponse({
            'workspace_id': workspace_id,
            'plugin_name': plugin_id,
            'node_count': graph.node_count(),
            'edge_count': graph.edge_count(),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def api_get_graph(request, workspace_id):
    workspace = platform.get_workspace(workspace_id)
    if not workspace:
        return JsonResponse({'error': 'Workspace not found'}, status=404)
    return JsonResponse(serialize_graph(workspace.graph))


def api_search_graph(request, workspace_id):
    query = request.GET.get('q', '')
    result = platform.search(workspace_id, query)
    if isinstance(result, str):
        return JsonResponse({'error': result}, status=400)
    return JsonResponse(serialize_graph(result))


@csrf_exempt
def api_filter_graph(request, workspace_id):
    data = json.loads(request.body)
    result = platform.filter(workspace_id, data.get('filter', ''))
    if isinstance(result, str):
        return JsonResponse({'error': result}, status=400)
    return JsonResponse(serialize_graph(result))

@csrf_exempt
def api_reset_graph(request, workspace_id):
    graph = platform.reset_workspace(workspace_id)
    if graph is None:
        return JsonResponse({'error': 'Workspace not found'}, status=404)
    return JsonResponse(serialize_graph(graph))

@csrf_exempt
def api_cli_graph(request, workspace_id):
    data = json.loads(request.body)
    command_str = (data.get('command') or '').strip()
    if not command_str:
        return JsonResponse({'error': 'No command provided'}, status=400)

    result = platform.execute_cli(workspace_id, command_str)
    if isinstance(result, str):
        return JsonResponse({'error': result}, status=400)

    workspace = platform.get_workspace(workspace_id)
    return JsonResponse(serialize_graph(workspace.graph))

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