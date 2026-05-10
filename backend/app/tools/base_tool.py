from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """Base interface for all tools."""

    name: str = "base_tool"
    description: str = "Abstract base tool"

    def __init__(self, name: str = None, description: str = None):
        if name:
            self.name = name
        if description:
            self.description = description

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with the provided input."""
        raise NotImplementedError("Tool must implement run().")
