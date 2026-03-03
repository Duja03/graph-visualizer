from typing import Dict

from api.model import Graph, Node, AttributeValue
from .command import Command


class CreateNodeCommand(Command):
    def __init__(self, graph: Graph, node_id: str, attributes: Dict[str, AttributeValue]):
        self.graph = graph
        self.node_id = node_id
        self.attributes = attributes

    def execute(self) -> None:
        node = Node(id=self.node_id, attributes=self.attributes)
        self.graph.add_node(node)


class EditNodeCommand(Command):
    def __init__(self, graph: Graph, node_id: str, attributes: Dict[str, AttributeValue]):
        self.graph = graph
        self.node_id = node_id
        self.attributes = attributes

    def execute(self) -> None:
        node = self.graph.get_node(self.node_id)
        for name, value in self.attributes.items():
            node.set_attribute(name, value)


class DeleteNodeCommand(Command):
    def __init__(self, graph: Graph, node_id: str):
        self.graph = graph
        self.node_id = node_id

    def execute(self) -> None:
        self.graph.remove_node(self.node_id)