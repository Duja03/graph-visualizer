"""
plugin_registry.py
Discovers and holds all installed DataSourcePlugin instances.
"""

import sys
import os

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
print("__file__:", os.path.abspath(__file__))
print("repo_root:", repo_root)  
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from typing import Dict, Optional, List


class PluginRegistry:
    def __init__(self):
        self._plugins: Dict[str, object] = {}
        self._discover()

    def _discover(self):
        from plugins.csv_datasource_plugin.csv_datasource_plugin import CsvDataSourcePlugin
        from plugins.json_datasource.json_datasource_plugin import JsonDataSourcePlugin
        for cls in [CsvDataSourcePlugin, JsonDataSourcePlugin]:
            self._plugins[cls.static_identifier] = cls

    def get_all_plugins(self) -> List:
        return list(self._plugins.values())

    def get_plugin(self, plugin_id: str) -> Optional[object]:
        return self._plugins.get(plugin_id)

    def register(self, plugin):
        self._plugins[plugin.plugin_id] = plugin