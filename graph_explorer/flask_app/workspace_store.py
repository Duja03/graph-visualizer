"""
workspace_store.py
In-memory store for active workspaces.
Each workspace holds a loaded graph and its source plugin reference.
"""

import uuid
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Workspace:
    workspace_id: str
    graph: object          # platform.model.Graph instance
    plugin: object         # DataSourcePlugin instance


class WorkspaceStore:
    def __init__(self):
        self._workspaces: Dict[str, Workspace] = {}

    def create_workspace(self, graph, plugin) -> str:
        workspace_id = str(uuid.uuid4())
        self._workspaces[workspace_id] = Workspace(
            workspace_id=workspace_id,
            graph=graph,
            plugin=plugin,
        )
        return workspace_id

    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        return self._workspaces.get(workspace_id)

    def list_workspaces(self):
        return list(self._workspaces.values())

    def delete_workspace(self, workspace_id: str) -> bool:
        if workspace_id in self._workspaces:
            del self._workspaces[workspace_id]
            return True
        return False