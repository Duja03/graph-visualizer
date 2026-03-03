from api.model import Graph
from .command import Command


class DeleteGraphCommand(Command):
    def __init__(self, graph: Graph):
        self.graph = graph

    def execute(self) -> None:
        for edge_id in list(self.graph.edges):
            self.graph.remove_edge(edge_id)
        for node_id in list(self.graph.nodes):
            self.graph.remove_node(node_id)