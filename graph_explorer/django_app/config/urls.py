from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_view, name='main'),
    path('tree/', views.tree_view, name='tree'),
    path('map/', views.map_view, name='map'),
    path('workspace/', views.workspace_view, name='workspace'),
]