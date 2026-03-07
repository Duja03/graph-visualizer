"""
plugin_registry.py
Auto-discovers installed plugins via importlib.metadata entry_points.

Datasource plugins must register under: graph_explorer.datasource_plugins
Visualizer plugins must register under:  graph_explorer.visualizer_plugins
"""

from importlib.metadata import entry_points
from typing import Optional
from api.plugins import DataSourcePlugin, VisualizerPlugin


DATASOURCE_GROUP = "graph_explorer.datasource_plugins"
VISUALIZER_GROUP = "graph_explorer.visualizer_plugins"


class PluginRegistry:
    def __init__(self):
        self._datasource_plugins: dict[str, type] = {}
        self._visualizer_plugins: dict[str, type] = {}
        self._discover()

    def _discover(self):
        for ep in entry_points(group=DATASOURCE_GROUP):
            try:
                plugin_class = ep.load()
                if not issubclass(plugin_class, DataSourcePlugin):
                    print(f"[PluginRegistry] '{ep.name}' does not implement DataSourcePlugin, skipping")
                    continue
                instance = plugin_class()
                self._datasource_plugins[instance.plugin_id()] = plugin_class
            except Exception as e:
                print(f"[PluginRegistry] Failed to load datasource plugin '{ep.name}': {e}")

        for ep in entry_points(group=VISUALIZER_GROUP):
            try:
                plugin_class = ep.load()
                if not issubclass(plugin_class, VisualizerPlugin):
                    print(f"[PluginRegistry] '{ep.name}' does not implement VisualizerPlugin, skipping")
                    continue
                instance = plugin_class()
                self._visualizer_plugins[instance.plugin_id()] = plugin_class
            except Exception as e:
                print(f"[PluginRegistry] Failed to load visualizer plugin '{ep.name}': {e}")

    def get_plugin(self, plugin_id: str) -> Optional[type]:
        return self._datasource_plugins.get(plugin_id)

    def get_all_datasource_plugins(self) -> list[type]:
        return list(self._datasource_plugins.values())

    def get_visualizer_plugin(self, plugin_id: str) -> Optional[type]:
        return self._visualizer_plugins.get(plugin_id)

    def get_all_visualizer_plugins(self) -> list[type]:
        return list(self._visualizer_plugins.values())