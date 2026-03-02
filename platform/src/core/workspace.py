import time

from api.model import Graph
from api.plugins import DataSourcePlugin
from api.plugins import VisualizerPlugin
from plugins.csv_datasource_plugin import CsvDataSourcePlugin
from plugins.json_datasource import JsonDataSourcePlugin
from plugins.xml_datasource_plugin import XmlDataSourcePlugin

data_sources = {
    CsvDataSourcePlugin.static_identifier: CsvDataSourcePlugin,
    JsonDataSourcePlugin.static_identifier: JsonDataSourcePlugin,
    XmlDataSourcePlugin.static_identifier: XmlDataSourcePlugin,
}

class Workspace:
    def __init__(self):
        self.__id: int = int(time.time())
        self.__filepath: str | None = ''
        self.__data_source_plugin: DataSourcePlugin | None = data_sources[JsonDataSourcePlugin.static_identifier]
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
        return self.__source_plugin

    @property
    def visualizer_plugin(self) -> VisualizerPlugin:
        return self.__visualizer_plugin

