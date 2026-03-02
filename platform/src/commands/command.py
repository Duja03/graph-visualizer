from __future__ import annotations
from abc import ABC, abstractmethod

from api.model import Graph


class Command(ABC):
    """
    The Command interface declares a method for executing a command
    """

    @abstractmethod
    def execute(self) -> None:
        pass
