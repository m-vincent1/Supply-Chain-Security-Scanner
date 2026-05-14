from pathlib import Path
import pytest

from app.parsers.python_parser import RequirementsTxtParser
from app.parsers.node_parser import PackageJsonParser
from app.parsers.maven_parser import PomXmlParser
from app.models.schemas import Ecosystem, DependencyType


def test_requirements_txt_parser(fixtures_dir):
    parser = RequirementsTxtParser()
    req_file = fixtures_dir / "requirements.txt"
    assert parser.can_parse(req_file)
    components = parser.parse(req_file)

    names = [c.name for c in components]
    assert "django" in names
    assert "flask" in names
    assert "requests" in names

    django = next(c for c in components if c.name == "django")
    assert django.version == "3.2.0"
    assert django.ecosystem == Ecosystem.python
    assert django.dependency_type == DependencyType.production
    assert django.is_pinned is True


def test_requirements_txt_ignores_comments(fixtures_dir):
    parser = RequirementsTxtParser()
    components = parser.parse(fixtures_dir / "requirements.txt")
    names = [c.name for c in components]
    assert not any(n.startswith("#") for n in names)


def test_package_json_parser(fixtures_dir):
    parser = PackageJsonParser()
    pkg_file = fixtures_dir / "package.json"
    assert parser.can_parse(pkg_file)
    components = parser.parse(pkg_file)

    prod_names = [c.name for c in components if c.dependency_type == DependencyType.production]
    dev_names = [c.name for c in components if c.dependency_type == DependencyType.development]

    assert "lodash" in prod_names
    assert "express" in prod_names
    assert "webpack" in dev_names
    assert "moment" in dev_names

    lodash = next(c for c in components if c.name == "lodash")
    assert lodash.version == "4.17.20"
    assert lodash.ecosystem == Ecosystem.npm


def test_pom_xml_parser(fixtures_dir):
    parser = PomXmlParser()
    pom_file = fixtures_dir / "pom.xml"
    assert parser.can_parse(pom_file)
    components = parser.parse(pom_file)

    names = [c.name for c in components]
    assert any("log4j" in n for n in names)
    assert any("spring-core" in n for n in names)
    assert any("jackson-databind" in n for n in names)

    log4j = next(c for c in components if "log4j" in c.name)
    assert log4j.version == "2.14.0"
    assert log4j.ecosystem == Ecosystem.maven


def test_pom_xml_test_scope(fixtures_dir):
    parser = PomXmlParser()
    components = parser.parse(fixtures_dir / "pom.xml")
    junit = next((c for c in components if "junit" in c.name), None)
    assert junit is not None
    assert junit.dependency_type == DependencyType.test
