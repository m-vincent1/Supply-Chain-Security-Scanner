import xml.etree.ElementTree as ET
from pathlib import Path

from app.models.schemas import Component, DependencyType, Ecosystem
from app.parsers.base import BaseParser


class PomXmlParser(BaseParser):
    """Parser for Maven pom.xml files."""

    MAVEN_NS = "http://maven.apache.org/POM/4.0.0"

    def can_parse(self, file_path: Path) -> bool:
        return file_path.name == "pom.xml"

    def parse(self, file_path: Path) -> list[Component]:
        components: list[Component] = []
        tree = ET.parse(file_path)
        root = tree.getroot()

        ns = self._detect_namespace(root)
        properties = self._extract_properties(root, ns)

        for dep in root.findall(f".//{ns}dependency"):
            group_id = self._get_text(dep, f"{ns}groupId")
            artifact_id = self._get_text(dep, f"{ns}artifactId")
            version_raw = self._get_text(dep, f"{ns}version")
            scope_raw = self._get_text(dep, f"{ns}scope") or "compile"

            if not artifact_id:
                continue

            name = f"{group_id}:{artifact_id}" if group_id else artifact_id
            version = self._resolve_property(version_raw, properties) if version_raw else None
            dep_type = self._scope_to_type(scope_raw)

            components.append(Component(
                name=name,
                version=version,
                ecosystem=Ecosystem.maven,
                source_file=str(file_path),
                dependency_type=dep_type,
                is_pinned=version is not None,
            ))

        return components

    def _detect_namespace(self, root: ET.Element) -> str:
        tag = root.tag
        if tag.startswith("{"):
            return "{" + tag[1:tag.index("}")] + "}"
        return ""

    def _extract_properties(self, root: ET.Element, ns: str) -> dict[str, str]:
        props: dict[str, str] = {}
        props_el = root.find(f"{ns}properties")
        if props_el is not None:
            for child in props_el:
                tag = child.tag.replace(ns, "")
                if child.text:
                    props[f"${{{tag}}}"] = child.text.strip()
        return props

    def _get_text(self, element: ET.Element, tag: str) -> str | None:
        child = element.find(tag)
        if child is not None and child.text:
            return child.text.strip()
        return None

    def _resolve_property(self, value: str, properties: dict[str, str]) -> str:
        return properties.get(value, value)

    def _scope_to_type(self, scope: str) -> DependencyType:
        mapping = {
            "compile": DependencyType.production,
            "runtime": DependencyType.production,
            "provided": DependencyType.production,
            "test": DependencyType.test,
            "import": DependencyType.development,
        }
        return mapping.get(scope.lower(), DependencyType.unknown)
