from __future__ import annotations

from api.model import Graph, Node


class SearchEngine:
    """
    Performs free-text search over a Graph and returns a subgraph.

    A node matches if any of the following contains the query string
    (case-insensitive):
        - an attribute key (name)
        - an attribute value (converted to str)

    The resulting subgraph is built via Graph.subgraph() which preserves
    edges only between matched nodes.
    """

    def __init__(self, graph: Graph) -> None:
        self._graph = graph

    def search(self, query: str) -> Graph:
        """
        Return a subgraph whose nodes match query.
        Args:
            query: Free-text search string (case-insensitive contains).
        Returns:
            A new Graph containing only matching nodes and edges between them.
        Raises:
            ValueError: If query is empty or whitespace-only.
        """
        query = query.strip()
        if not query:
            raise ValueError("Search query must not be empty.")

        q = query.lower()

        matched_ids = {
            node.id
            for node in self._graph.nodes.values()
            if self._node_matches(node, q)
        }

        return self._graph.subgraph(matched_ids)

    @staticmethod
    def _node_matches(node: Node, query_lower: str) -> bool:
        """Return True if any attribute key or value contains the query."""
        for key, value in node.attributes.items():
            if query_lower in key.lower():
                return True
            if query_lower in str(value).lower():
                return True
        return False