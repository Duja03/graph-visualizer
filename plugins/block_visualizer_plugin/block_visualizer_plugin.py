import json
import os

from api.model import Graph
from api.plugins import VisualizerPlugin

class BlockVisualizerPlugin(VisualizerPlugin):

    static_identifier = "BLOCK"

    def plugin_id(self) -> str:
        return "block_visualizer"

    def name(self) -> str:
        return "Block Visualizer"

    def render(self, graph: Graph) -> str:
        if graph is None:
            graph_data = {'nodes': [], 'edges': []}
        else:
            serialized_nodes = [
                {'id': node.id, 'attributes': node.attributes}
                for node in graph.nodes.values()
            ]

            serialized_edges = [
                {'id': edge.id, 'source': edge.source, 'target': edge.target, 'value': edge.attributes}
                for edge in graph.edges.values()
            ]

            graph_data = {
                'nodes': serialized_nodes,
                'edges': serialized_edges
            }

        graph_json = json.dumps(graph_data)

        template_path = os.path.join(os.path.dirname(__file__), 'block_visualizer_template.html')
        with open(template_path, 'r') as f:
            html = f.read()

        html = html.replace('{% load static %}', '')
        html = html.replace("{{ graph_json | safe }}", graph_json)

        return html
