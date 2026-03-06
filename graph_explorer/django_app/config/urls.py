from django.shortcuts import redirect
from django.urls import path
from django.urls.conf import re_path

from . import views

urlpatterns = [
    # Template views
    path('', views.main_view, name='main'),
    path('workspace/', views.workspace_view, name='workspace'),

    # API endpoints (replaces Flask)
    path('api/plugins/datasource', views.api_datasource_plugins),
    path('api/plugins/visualizer', views.api_visualizer_plugins),
    path('api/plugins/<str:plugin_id>/params', views.api_plugin_params),
    path('api/graph/load', views.api_load_graph),
    path('api/graph/<str:workspace_id>', views.api_get_graph),
    path('api/graph/<str:workspace_id>/search', views.api_search_graph),
    path('api/graph/<str:workspace_id>/filter', views.api_filter_graph),
    path('api/graph/<str:workspace_id>/reset', views.api_reset_graph),
    path('api/graph/<str:workspace_id>/cli', views.api_cli_graph),

    re_path(r'^.*$', lambda request: redirect('main', permanent=False)),
]