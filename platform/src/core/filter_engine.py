import re
import operator
from datetime import date
from typing import Set

from api.model import Graph, AttributeValue

OPERATORS = {
    '==': operator.eq,
    '!=': operator.ne,
    '>':  operator.gt,
    '>=': operator.ge,
    '<':  operator.lt,
    '<=': operator.le,
}


class FilterError(ValueError):
    pass


def _parse_value(raw: str, target_type: type) -> AttributeValue:
    try:
        if target_type == int:
            return int(raw)
        if target_type == float:
            return float(raw)
        if target_type == date:
            return date.fromisoformat(raw)
        return raw
    except (ValueError, TypeError):
        raise FilterError(
            f"Cannot parse '{raw}' as {target_type.__name__}"
        )


class FilterEngine:

    @staticmethod
    def filter(graph: Graph, filter_str: str) -> Graph:
        """
        Takes filter string (e.g. 'Age > 30')
        Returns subgraph which nodes satisfy condition.
        """
        pattern = r'^\s*(\w+)\s*(==|!=|>=|<=|>|<)\s*(.+?)\s*$'
        match = re.match(pattern, filter_str.strip())
        if not match:
            raise FilterError(
                f"Invalid filter format. Expected: '<attr> <op> <value>'. Got: '{filter_str}'"
            )

        attr_name, op_str, raw_value = match.groups()
        op = OPERATORS[op_str]

        matching_ids: Set[str] = set()

        for node in graph:
            attr = node.get_attribute(attr_name)
            if attr is None:
                continue
            try:
                parsed_value = _parse_value(raw_value, type(attr))
                if op(attr, parsed_value):
                    matching_ids.add(node.id)
            except FilterError:
                raise FilterError(
                    f"Type mismatch: attribute '{attr_name}' is {type(attr).__name__}, "
                    f"cannot compare with '{raw_value}'"
                )

        return graph.subgraph(matching_ids)