from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class Command(ABC):
    """
    The Command interface declares a method for executing a command
    """

    @abstractmethod
    def execute(self) -> Any:
        pass
