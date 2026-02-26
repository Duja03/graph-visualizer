from enum import Enum
from datetime import date
from typing import Union


class AttributeType(Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    DATE = "date"


AttributeValue = Union[
    int,
    float,
    str,
    date
]