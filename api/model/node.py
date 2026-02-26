from dataclasses import dataclass, field
from typing import Dict
from api.types import AttributeValue


@dataclass(slots=True)
class Node:
    id: str
    attributes: Dict[str, AttributeValue] = field(default_factory=dict)

    def set_attribute(self, name: str, value: AttributeValue):
        self.attributes[name] = value