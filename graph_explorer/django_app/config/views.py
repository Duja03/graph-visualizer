"""
Thin Django views — each view only renders a template and passes minimal context.
All data logic is delegated to the Flask API (flask_app microservice).
"""

from django.shortcuts import render
from django.conf import settings


def main_view(request):
    """Main View: central graph canvas with pan/zoom/drag-drop."""
    return render(request, 'main.html', {
        'flask_api_url': settings.FLASK_API_URL,
        'active_view': 'main',
    })


def tree_view(request):
    """Tree View: package-flask_app-style collapsible tree."""
    return render(request, 'tree-view.html', {
        'flask_api_url': settings.FLASK_API_URL,
        'active_view': 'tree',
    })


def map_view(request):
    """Bird View (map): minimap overview of the full graph."""
    return render(request, 'map-view.html', {
        'flask_api_url': settings.FLASK_API_URL,
        'active_view': 'map',
    })


def workspace_view(request):
    """Workspace selector: choose data source plugin and load graph."""
    return render(request, 'workspace.html', {
        'flask_api_url': settings.FLASK_API_URL,
        'active_view': 'workspace',
    })