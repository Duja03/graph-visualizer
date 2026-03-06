"""
workspace_store.py
In-memory store for active workspaces.
"""
import uuid
from typing import Dict, Optional
from .workspace import Workspace

class WorkspaceStore:
    def __init__(self):
        self._workspaces: Dict[str, Workspace] = {}

    def create_workspace(self, graph, data_source_plugin, visualizer_plugin, filepath: str = '') -> str:
        workspace_id = str(uuid.uuid4())
        ws = Workspace(data_source_plugin=data_source_plugin, visualizer_plugin=visualizer_plugin)
        ws.id = workspace_id
        ws.filepath = filepath
        ws.graph = graph
        ws.initial_graph = graph
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