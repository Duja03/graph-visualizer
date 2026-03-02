from typing import Dict
from api.model import Graph, Node, AttributeValue
from command import Command


class CreateNodeCommand(Command):
    def __init__(self, graph: Graph, node_id: str, attributes: Dict[str, AttributeValue]):
        self.graph = graph
        self.node_id = node_id
        self.attributes = attributes

    def execute(self) -> None:
        pass


class EditNodeCommand(Command):
    def __init__(self, graph: Graph, node_id: str, attributes: Dict[str, AttributeValue]):
        self.graph = graph
        self.node_id = node_id
        self.attributes = attributes

    def execute(self) -> None:
        pass


class DeleteNodeCommand(Command):
    def __init__(self, graph: Graph, node_id: str):
        self.graph = graph
        self.node_id = node_id

    def execute(self) -> None:
        pass