from typing import Dict

from workspace import Workspace

class Platform:
    def __init__(self):
        self.__workspaces: Dict[int, Workspace] = {}

    def add_workspace(self, workspace: Workspace):
        self.__workspaces[workspace.id] = workspace

    def get_workspace(self, workspace_id: int) -> Workspace:
        return self.__workspaces.get(workspace_id, Workspace())