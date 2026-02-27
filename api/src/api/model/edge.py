from dataclasses import dataclass, field
from typing import Dict
from .attribute_type import AttributeValue

@dataclass(slots=True)
class Edge:
    id: str
    source: str
    target: str
    attributes: Dict[str, AttributeValue] = field(default_factory=dict)

    def set_attribute(self, name: str, value: AttributeValue):
        self.attributes[name] = value