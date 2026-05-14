from pathlib import Path

from app.models.schemas import Component
from app.parsers.base import BaseParser
from app.parsers.python_parser import RequirementsTxtParser, PyprojectTomlParser
from app.parsers.node_parser import PackageJsonParser
from app.parsers.maven_parser import PomXmlParser

_PARSERS: list[BaseParser] = [
    RequirementsTxtParser(),
    PyprojectTomlParser(),
    PackageJsonParser(),
    PomXmlParser(),
]

SUPPORTED_FILES = {
    "requirements.txt", "requirements-dev.txt", "requirements-test.txt",
    "pyproject.toml",
    "package.json",
    "pom.xml",
}


def detect_and_parse(project_path: Path) -> list[Component]:
    """Recursively scan a project directory and parse all supported dependency files."""
    components: list[Component] = []
    for file_path in project_path.rglob("*"):
        if not file_path.is_file():
            continue
        if _should_skip(file_path):
            continue
        for parser in _PARSERS:
            if parser.can_parse(file_path):
                try:
                    parsed = parser.parse(file_path)
                    components.extend(parsed)
                except Exception:
                    pass
                break
    return components


def _should_skip(path: Path) -> bool:
    skip_dirs = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build", ".tox"}
    return any(part in skip_dirs for part in path.parts)
