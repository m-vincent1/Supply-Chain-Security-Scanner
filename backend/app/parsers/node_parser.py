import json
import re
from pathlib import Path

from app.models.schemas import Component, DependencyType, Ecosystem
from app.parsers.base import BaseParser


class PackageJsonParser(BaseParser):
    """Parser for package.json files."""

    def can_parse(self, file_path: Path) -> bool:
        return file_path.name == "package.json"

    def parse(self, file_path: Path) -> list[Component]:
        components: list[Component] = []
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        for name, version_spec in data.get("dependencies", {}).items():
            components.append(Component(
                name=name,
                version=self._extract_version(version_spec),
                ecosystem=Ecosystem.npm,
                source_file=str(file_path),
                dependency_type=DependencyType.production,
                is_pinned=self._is_pinned(version_spec),
            ))

        for name, version_spec in data.get("devDependencies", {}).items():
            components.append(Component(
                name=name,
                version=self._extract_version(version_spec),
                ecosystem=Ecosystem.npm,
                source_file=str(file_path),
                dependency_type=DependencyType.development,
                is_pinned=self._is_pinned(version_spec),
            ))

        for name, version_spec in data.get("peerDependencies", {}).items():
            components.append(Component(
                name=name,
                version=self._extract_version(version_spec),
                ecosystem=Ecosystem.npm,
                source_file=str(file_path),
                dependency_type=DependencyType.production,
                is_pinned=self._is_pinned(version_spec),
            ))

        return components

    def _extract_version(self, version_spec: str) -> str | None:
        if not version_spec:
            return None
        cleaned = re.sub(r"^[^0-9]*", "", version_spec)
        m = re.match(r"^(\d+\.\d+(?:\.\d+)?)", cleaned)
        if m:
            return m.group(1)
        return version_spec if version_spec not in ("*", "latest", "x") else None

    def _is_pinned(self, version_spec: str) -> bool:
        if not version_spec or version_spec in ("*", "latest", "x"):
            return False
        return not bool(re.match(r"^[\^~]", version_spec))
