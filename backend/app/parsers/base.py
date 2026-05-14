from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from app.models.schemas import Component


class BaseParser(ABC):
    """Base class for all dependency file parsers."""

    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """Return True if this parser can handle the given file."""

    @abstractmethod
    def parse(self, file_path: Path) -> list[Component]:
        """Parse a dependency file and return a list of components."""

    @staticmethod
    def _normalize_version(version: Optional[str]) -> Optional[str]:
        if not version:
            return None
        return version.strip().lstrip("=^~v")
