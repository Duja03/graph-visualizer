import time
from api.src.api.model.graph import Graph
from api.src.api.plugins.datasource_plugin import DataSourcePlugin
from api.src.api.plugins.visualizer_plugin import VisualizerPlugin


class Workspace:
    def __init__(self, data_source_plugin: DataSourcePlugin = None):
        self.__id: int = int(time.time())
        self.__filepath: str = ''
        self.__data_source_plugin: DataSourcePlugin | None = data_source_plugin
        self.__visualizer_plugin: VisualizerPlugin | None = None
        self.__graph: Graph | None = None
        self.__initial_graph: Graph | None = None

    @property
    def id(self) -> int:
        return self.__id

    @property
    def filepath(self) -> str:
        return self.__filepath

    @filepath.setter
    def filepath(self, filepath: str) -> None:
        self.__filepath = filepath

    @property
    def source_plugin(self) -> DataSourcePlugin:
        return self.__data_source_plugin

    @property
    def visualizer_plugin(self) -> VisualizerPlugin:
        return self.__visualizer_plugin

    @property
    def graph(self) -> Graph:
        return self.__graph

    @graph.setter
    def graph(self, graph: Graph) -> None:
        self.__graph = graph

    @property
    def initial_graph(self) -> Graph:
        return self.__initial_graph

    @initial_graph.setter
    def initial_graph(self, graph: Graph) -> None:
        self.__initial_graph = graph