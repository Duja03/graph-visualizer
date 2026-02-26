from abc import abstractmethod
from typing import Dict, Any

from api.model.graph import Graph
from api.plugins.base_plugin import Plugin


class DataSourcePlugin(Plugin):
    """
    Base abstraction for all data source plugins.

    Responsibility:
    - parse external data source
    - construct Graph model
    """

    @abstractmethod
    def parameters(self) -> Dict[str, str]:
        """
        Defines required input parameters.

        Example:
        {
            "file_path": "Path to JSON file"
        }
        """
        raise NotImplementedError

    @abstractmethod
    def load(self, **kwargs: Any) -> Graph:
        """
        Parse data source and construct graph.

        kwargs contain user provided parameters.
        """
        raise NotImplementedError