import pytest
from pathlib import Path

from app.services.scan_service import run_scan


SAMPLE_PROJECTS = Path(__file__).parent.parent.parent / "sample-projects"


@pytest.mark.skipif(not (SAMPLE_PROJECTS / "python-vulnerable").exists(), reason="sample projects not available")
def test_scan_vulnerable_python_project():
    result = run_scan(SAMPLE_PROJECTS / "python-vulnerable")
    assert result.total_dependencies > 0
    assert result.total_vulnerabilities > 0
    assert result.risk_score.total > 20


@pytest.mark.skipif(not (SAMPLE_PROJECTS / "python-secure").exists(), reason="sample projects not available")
def test_scan_secure_python_project():
    result = run_scan(SAMPLE_PROJECTS / "python-secure")
    assert result.total_dependencies > 0
    assert result.total_vulnerabilities == 0
    assert result.risk_score.total < 30


def test_scan_fixture_project(fixtures_dir, tmp_path):
    import shutil
    shutil.copy(fixtures_dir / "requirements.txt", tmp_path / "requirements.txt")
    result = run_scan(tmp_path, project_name="test-project")
    assert result.project_name == "test-project"
    assert result.total_dependencies > 0
    assert len(result.components) > 0
    assert len(result.sbom.components) == result.total_dependencies


def test_scan_generates_sbom(fixtures_dir, tmp_path):
    import shutil
    shutil.copy(fixtures_dir / "requirements.txt", tmp_path / "requirements.txt")
    result = run_scan(tmp_path)
    assert result.sbom.project_name == tmp_path.name
    assert len(result.sbom.components) > 0
    assert result.sbom.scanner_version == "1.0.0"


def test_scan_nonexistent_path():
    with pytest.raises(FileNotFoundError):
        run_scan(Path("/nonexistent/path/that/does/not/exist"))
