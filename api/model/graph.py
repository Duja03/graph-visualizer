from typing import Dict, Set, Iterable

from api.graph.node import Node
from api.graph.edge import Edge


class Graph:

    def __init__(
        self,
        directed: bool = True
    ):
        self.directed = directed

        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}

        # adjacency
        self._outgoing: Dict[str, Set[str]] = {}
        self._incoming: Dict[str, Set[str]] = {}

    # node operations

    def add_node(self, node: Node):

        if node.id in self.nodes:
            raise ValueError("Node already exists")

        self.nodes[node.id] = node
        self._outgoing[node.id] = set()
        self._incoming[node.id] = set()

    def get_node(self, node_id: str) -> Node:
        return self.nodes[node_id]

    # edge operations

    def add_edge(self, edge: Edge):

        if edge.id in self.edges:
            raise ValueError("Edge exists")

        if edge.source not in self.nodes:
            raise ValueError("Source missing")

        if edge.target not in self.nodes:
            raise ValueError("Target missing")

        self.edges[edge.id] = edge

        self._outgoing[edge.source].add(edge.id)
        self._incoming[edge.target].add(edge.id)

        if not self.directed:
            self._outgoing[edge.target].add(edge.id)
            self._incoming[edge.source].add(edge.id)

    # neighbor operations

    def neighbors(self, node_id: str) -> Iterable[Node]:

        for edge_id in self._outgoing[node_id]:

            edge = self.edges[edge_id]

            yield self.nodes[edge.target]

    # delete operations

    def remove_edge(self, edge_id: str):

        edge = self.edges.pop(edge_id)

        self._outgoing[edge.source].remove(edge_id)
        self._incoming[edge.target].remove(edge_id)

    def remove_node(self, node_id: str):

        if self._incoming[node_id] or self._outgoing[node_id]:
            raise ValueError(
                "Node connected with edges"
            )

        del self.nodes[node_id]
        del self._incoming[node_id]
        del self._outgoing[node_id]

    # info & iteration

    def node_count(self) -> int:
    return len(self.nodes)


    def edge_count(self) -> int:
        return len(self.edges)


    def __len__(self):
        return len(self.nodes)


    def __iter__(self):
        return iter(self.nodes.values())


    def iter_edges(self):
        return iter(self.edges.values())