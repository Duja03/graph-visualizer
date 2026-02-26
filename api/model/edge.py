from dataclasses import dataclass, field
from typing import Dict
from api.types import AttributeValue


@dataclass(slots=True)
class Edge:
    id: str
    source: str
    target: str
    attributes: Dict[str, AttributeValue] = field(default_factory=dict)