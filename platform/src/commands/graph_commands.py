from api.model import Graph
from command import Command


class DeleteGraphCommand(Command):
    def __init__(self, graph: Graph):
        self.graph = graph

    def execute(self) -> None:
        pass