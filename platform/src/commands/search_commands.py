from api.model import Graph
from .command import Command
from core.search_engine import SearchEngine


class SearchCommand(Command):
    def __init__(self, graph: Graph, query: str):
        self.graph = graph
        self.query = query

    def execute(self) -> Graph:
        return SearchEngine(self.graph).search(self.query)