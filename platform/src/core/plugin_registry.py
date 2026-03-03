# platform/src/core/plugin_registry.py
from importlib.metadata import entry_points
from typing import Dict, Optional, List

class PluginRegistry:
    def __init__(self):
        self._plugins: Dict[str, object] = {}
        self._discover()

    def _discover(self):
        eps = entry_points(group='graph_explorer.datasource_plugins')
        for ep in eps:
            cls = ep.load()
            self._plugins[cls.static_identifier] = cls

    def get_all_plugins(self) -> List:
        return list(self._plugins.values())

    def get_plugin(self, plugin_id: str) -> Optional[object]:
        return self._plugins.get(plugin_id)