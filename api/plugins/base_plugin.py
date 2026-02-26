from abc import ABC, abstractmethod


class Plugin(ABC):
    """
    Base abstraction for all plugins.

    Every plugin must provide:
    - stable unique identifier
    - human readable name
    """

    @abstractmethod
    def plugin_id(self) -> str:
        """
        Unique stable plugin identifier.
        Used for plugin registration and lookup.
        """
        raise NotImplementedError

    @abstractmethod
    def name(self) -> str:
        """
        Human readable plugin name.
        """
        raise NotImplementedError