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
        from plugins.csv_datasource_plugin import CsvDataSourcePlugin
        from plugins.json_datasource import JsonDataSourcePlugin
        for cls in [CsvDataSourcePlugin, JsonDataSourcePlugin]:
            self._plugins[cls.static_identifier] = cls

    def get_all_plugins(self) -> List:
        return list(self._plugins.values())

    def get_plugin(self, plugin_id: str) -> Optional[object]:
        return self._plugins.get(plugin_id)

    def register(self, plugin):
        """Manually register a plugin (useful for testing)."""
        self._plugins[plugin.plugin_id] = plugin