from abc import abstractmethod

from ..model.graph import Graph
from .base_plugin import Plugin


class VisualizerPlugin(Plugin):
    """
    Visualization plugin abstraction.

    Responsible for generating HTML
    representation of graph.
    """

    @abstractmethod
    def render(self, graph: Graph) -> str:
        """
        Generate HTML representation
        of provided graph.

        Returns:
            HTML string
        """
        raise NotImplementedError