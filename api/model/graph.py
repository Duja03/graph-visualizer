from typing import Dict, Set, Iterable

from api.model.node import Node
from api.model.edge import Edge


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
            raise ValueError(f"Source node '{edge.source}' not found")

        if edge.target not in self.nodes:
            raise ValueError(f"Target node '{edge.target}' not found")

        self.edges[edge.id] = edge

        self._outgoing[edge.source].add(edge.id)
        self._incoming[edge.target].add(edge.id)

        if not self.directed:
            self._outgoing[edge.target].add(edge.id)
            self._incoming[edge.source].add(edge.id)

    def get_edge(self, edge_id: str) -> Edge:
        if edge_id not in self.edges:
            raise ValueError(f"Edge '{edge_id}' does not exist")
        return self.edges[edge_id]

    # neighbor operations

    def neighbors(self, node_id: str) -> Iterable[Node]:

        if node_id not in self.nodes:
            raise ValueError(f"Node '{node_id}' does not exist")

        for edge_id in self._outgoing[node_id]:

            edge = self.edges[edge_id]

            if edge.source == node_id:
                yield self.nodes[edge.target]
            else:
                yield self.nodes[edge.source]

    # delete operations

    def remove_edge(self, edge_id: str):

        if edge_id not in self.edges:
            raise ValueError(f"Edge '{edge_id}' does not exist")

        edge = self.edges.pop(edge_id)

        self._outgoing[edge.source].remove(edge_id)
        self._incoming[edge.target].remove(edge_id)
        if not self.directed:
            self._outgoing[edge.target].remove(edge_id)
            self._incoming[edge.source].remove(edge_id)

    def remove_node(self, node_id: str):

        if self._incoming[node_id] or self._outgoing[node_id]:
            raise ValueError(
                f"Node '{node_id}' is connected with edges"
            )

        del self.nodes[node_id]
        del self._incoming[node_id]
        del self._outgoing[node_id]

    # info & iteration

    def node_count(self) -> int:
        return len(self.nodes)

    def edge_count(self) -> int:
        return len(self.edges)

    def has_edge(self, edge_id: str) -> bool:
        return edge_id in self.edges

    def has_node(self, node_id: str) -> bool:
        return node_id in self.nodes

    def __len__(self):
        return len(self.nodes)

    @property
    def is_directed(self) -> bool:
        return self.directed

    def __iter__(self):
        return iter(self.nodes.values())


    def iter_edges(self):
        return iter(self.edges.values())

    # subgraph logic

    def subgraph(self, node_ids: Set[str]) -> "Graph":
        new_graph = Graph(directed=self.directed)
        # copy nodes
        for node_id in node_ids:
            if node_id in self.nodes:
                new_graph.add_node(self.nodes[node_id])
        # copy edges connecting selected nodes
        for edge in self.edges.values():
            if (edge.source in node_ids and edge.target in node_ids):
                new_graph.add_edge(edge)

        return new_graph