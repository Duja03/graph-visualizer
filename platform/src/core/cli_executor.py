from typing import Any

from commands.command import Command
from core.filter_engine import FilterError


class CLIExecutor:

    @staticmethod
    def execute(command: Command) -> Any:
        """
        Execute a given Command.

        Args:
            command: A Command instance.

        Returns:
            - None for mutating commands (create, edit, delete)
            - Graph subgraph for filter and search commands
            - str error message if execution fails
        """
        try:
            return command.execute()
        except FilterError as e:
            return f"Filter error: {e}"
        except (ValueError, KeyError) as e:
            return f"Error: {e}"