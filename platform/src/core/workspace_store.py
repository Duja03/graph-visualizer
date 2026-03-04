"""
workspace_store.py
In-memory store for active workspaces.
"""
import uuid
from typing import Dict, Optional

class WorkspaceStore:
    def __init__(self):
        self._workspaces: Dict[str, Workspace] = {}

    def create_workspace(self, graph, plugin, filepath: str = '') -> str:
        workspace_id = str(uuid.uuid4())
        ws = Workspace(data_source_plugin=plugin)
        ws.filepath = filepath
        ws._Workspace__graph = graph
        ws._Workspace__initial_graph = graph
        ws._Workspace__id = workspace_id
        self._workspaces[workspace_id] = ws
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