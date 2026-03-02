from typing import Dict
from api.model import Graph, Edge, AttributeValue
from command import Command


class CreateEdgeCommand(Command):
    def __init__(self, graph: Graph, edge_id: str, source: str, target: str, attributes: Dict[str, AttributeValue]):
        self.graph = graph
        self.edge_id = edge_id
        self.source = source
        self.target = target
        self.attributes = attributes

    def execute(self) -> None:
        pass


class EditEdgeCommand(Command):
    def __init__(self, graph: Graph, edge_id: str, attributes: Dict[str, AttributeValue]):
        self.graph = graph
        self.edge_id = edge_id
        self.attributes = attributes

    def execute(self) -> None:
        pass


class DeleteEdgeCommand(Command):
    def __init__(self, graph: Graph, edge_id: str):
        self.graph = graph
        self.edge_id = edge_id

    def execute(self) -> None:
        pass