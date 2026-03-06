from typing import Optional, Union

from api.model import Graph
from .workspace import Workspace
from .workspace_store import WorkspaceStore


class Platform:
    def __init__(self):
        self._store = WorkspaceStore()

    def create_workspace(self, graph: Graph, plugin, filepath: str = '') -> str:
        return self._store.create_workspace(graph, plugin, filepath)

    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        return self._store.get_workspace(workspace_id)

    def list_workspaces(self) -> list[Workspace]:
        return self._store.list_workspaces()

    def delete_workspace(self, workspace_id: str) -> bool:
        return self._store.delete_workspace(workspace_id)

    def reset_workspace(self, workspace_id: str) -> Optional[Graph]:
        """Restore the workspace graph to the originally loaded graph."""
        workspace = self._store.get_workspace(workspace_id)
        if workspace is None:
            return None
        workspace.graph = workspace.initial_graph
        return workspace.graph

    def search(self, workspace_id: str, query: str) -> Union[Graph, str]:
        """
        Run a free-text search against the active workspace graph.
        Updates workspace.graph to the resulting subgraph.
        Returns the subgraph, or an error string on failure.
        """
        from .search_engine import SearchEngine

        workspace = self._store.get_workspace(workspace_id)
        if workspace is None:
            return f"Error: workspace '{workspace_id}' not found"
        try:
            subgraph = SearchEngine(workspace.graph).search(query)
            workspace.graph = subgraph
            return subgraph
        except ValueError as e:
            return f"Error: {e}"

    def filter(self, workspace_id: str, filter_expr: str) -> Union[Graph, str]:
        """
        Apply a filter expression against the active workspace graph.
        Updates workspace.graph to the resulting subgraph.
        Returns the subgraph, or an error string on failure.
        """
        from .filter_engine import FilterEngine, FilterError

        workspace = self._store.get_workspace(workspace_id)
        if workspace is None:
            return f"Error: workspace '{workspace_id}' not found"
        try:
            subgraph = FilterEngine.filter(workspace.graph, filter_expr)
            workspace.graph = subgraph
            return subgraph
        except FilterError as e:
            return f"Filter error: {e}"

    def execute_cli(self, workspace_id: str, command_str: str) -> Union[None, Graph, str]:
        """
        Parse and execute a CLI command string against the active graph.

        Returns:
            None   — mutating command succeeded; workspace.graph modified in-place.
            Graph  — filter/search command succeeded; workspace.graph updated.
            str    — error message; workspace.graph left unchanged.
        """
        from core.cli_parser import CLIParser, CLIParseError
        from core.cli_executor import CLIExecutor

        workspace = self._store.get_workspace(workspace_id)
        if workspace is None:
            return f"Error: workspace '{workspace_id}' not found"

        try:
            cmd = CLIParser.parse(command_str, workspace.graph)
        except CLIParseError as e:
            return f"Parse error: {e}"

        if cmd is None:
            return "Error: unknown command"

        result = CLIExecutor.execute(cmd)

        if isinstance(result, str):
            return result

        if isinstance(result, Graph):
            workspace.graph = result
            return result

        return None