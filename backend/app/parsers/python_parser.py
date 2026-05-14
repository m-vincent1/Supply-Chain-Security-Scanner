import re
import tomllib
from pathlib import Path
from typing import Optional

from app.models.schemas import Component, DependencyType, Ecosystem
from app.parsers.base import BaseParser


class RequirementsTxtParser(BaseParser):
    """Parser for requirements.txt files."""

    COMMENT_RE = re.compile(r"\s*#.*$")
    REQUIREMENT_RE = re.compile(
        r"^([A-Za-z0-9_\-\.]+)\s*([><=!~^][><=!~^]?\s*[^\s,;]+(?:\s*,\s*[><=!~^][><=!~^]?\s*[^\s,;]+)*)?"
    )

    def can_parse(self, file_path: Path) -> bool:
        return file_path.name.lower() in ("requirements.txt", "requirements-dev.txt", "requirements-test.txt")

    def parse(self, file_path: Path) -> list[Component]:
        components: list[Component] = []
        dep_type = DependencyType.development if "dev" in file_path.name or "test" in file_path.name else DependencyType.production

        with open(file_path, encoding="utf-8") as f:
            for line_num, raw_line in enumerate(f, start=1):
                line = self.COMMENT_RE.sub("", raw_line).strip()
                if not line or line.startswith("-r") or line.startswith("--"):
                    continue

                match = self.REQUIREMENT_RE.match(line)
                if not match:
                    continue

                name = match.group(1)
                version_spec = match.group(2)
                pinned_version = self._extract_pinned(version_spec)
                is_pinned = pinned_version is not None

                components.append(
                    Component(
                        name=name,
                        version=pinned_version,
                        ecosystem=Ecosystem.python,
                        source_file=str(file_path),
                        dependency_type=dep_type,
                        line_number=line_num,
                        is_pinned=is_pinned,
                    )
                )
        return components

    def _extract_pinned(self, version_spec: Optional[str]) -> Optional[str]:
        if not version_spec:
            return None
        exact = re.match(r"^==\s*([\d\.]+)", version_spec.strip())
        if exact:
            return exact.group(1)
        loose = re.match(r"^[><=!~^]+\s*([\d\.]+(?:\.\d+)*)", version_spec.strip())
        if loose:
            return loose.group(1)
        return None


class PyprojectTomlParser(BaseParser):
    """Parser for pyproject.toml files."""

    def can_parse(self, file_path: Path) -> bool:
        return file_path.name == "pyproject.toml"

    def parse(self, file_path: Path) -> list[Component]:
        components: list[Component] = []
        with open(file_path, "rb") as f:
            data = tomllib.load(f)

        dependencies = (
            data.get("project", {}).get("dependencies", [])
            or data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        )

        if isinstance(dependencies, list):
            for dep in dependencies:
                name, version = self._parse_pep508(dep)
                if name:
                    components.append(Component(
                        name=name, version=version,
                        ecosystem=Ecosystem.python,
                        source_file=str(file_path),
                        dependency_type=DependencyType.production,
                        is_pinned=version is not None,
                    ))

        elif isinstance(dependencies, dict):
            for name, spec in dependencies.items():
                if name.lower() == "python":
                    continue
                version = spec if isinstance(spec, str) else None
                pinned = self._extract_version_from_spec(version)
                components.append(Component(
                    name=name, version=pinned,
                    ecosystem=Ecosystem.python,
                    source_file=str(file_path),
                    dependency_type=DependencyType.production,
                    is_pinned=pinned is not None,
                ))

        dev_deps = (
            data.get("tool", {}).get("poetry", {}).get("dev-dependencies", {})
        )
        for name, spec in dev_deps.items():
            version = spec if isinstance(spec, str) else None
            pinned = self._extract_version_from_spec(version)
            components.append(Component(
                name=name, version=pinned,
                ecosystem=Ecosystem.python,
                source_file=str(file_path),
                dependency_type=DependencyType.development,
                is_pinned=pinned is not None,
            ))

        return components

    def _parse_pep508(self, dep_str: str):
        match = re.match(r"^([A-Za-z0-9_\-\.]+)\s*([><=!~^].*)?$", dep_str.strip())
        if not match:
            return None, None
        name = match.group(1)
        spec = match.group(2)
        version = self._extract_version_from_spec(spec)
        return name, version

    def _extract_version_from_spec(self, spec: Optional[str]) -> Optional[str]:
        if not spec:
            return None
        m = re.search(r"[\d]+\.[\d]+(?:\.[\d]+)*", spec)
        return m.group(0) if m else None
