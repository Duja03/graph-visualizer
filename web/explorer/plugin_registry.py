"""
plugin_registry.py
Discovers and holds all installed DataSourcePlugin instances.
Plugins are found via Python's entry_points mechanism (or Django AppConfig equivalent).
"""

from typing import Dict, Optional, List


class PluginRegistry:
    """
    Discovers installed data source plugins.
    Plugins register themselves via the 'graph_explorer.datasource_plugins'
    entry point group in their setup.cfg / pyproject.toml.
    """

    def __init__(self):
        self._plugins: Dict[str, object] = {}
        self._discover()

    def _discover(self):
        try:
            from importlib.metadata import entry_points
            eps = entry_points(group='graph_explorer.datasource_plugins')
            for ep in eps:
                plugin_cls = ep.load()
                instance = plugin_cls()
                self._plugins[instance.plugin_id] = instance
        except Exception as e:
            # During development with no plugins installed yet, this is expected
            print(f'[PluginRegistry] Discovery warning: {e}')

    def get_all_plugins(self) -> List:
        return list(self._plugins.values())

    def get_plugin(self, plugin_id: str) -> Optional[object]:
        return self._plugins.get(plugin_id)

    def register(self, plugin):
        """Manually register a plugin (useful for testing)."""
        self._plugins[plugin.plugin_id] = plugin