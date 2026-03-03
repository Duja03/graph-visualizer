from api.model import Graph
from .command import Command
from core.filter_engine import FilterEngine


class FilterCommand(Command):
    def __init__(self, graph: Graph, filter_str: str):
        self.graph = graph
        self.filter_str = filter_str

    def execute(self) -> Graph:
        return FilterEngine.filter(self.graph, self.filter_str)