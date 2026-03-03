from api.model import Graph
from api.plugins import VisualizerPlugin


class BlockVisualizerPlugin(VisualizerPlugin):
    def render(self, graph: Graph) -> str:
        raise NotImplementedError