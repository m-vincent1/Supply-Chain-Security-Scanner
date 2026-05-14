import pytest
from pathlib import Path
from typer.testing import CliRunner
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from scs_scanner.main import app

runner = CliRunner()
SAMPLE_PROJECTS = Path(__file__).parent.parent.parent / "sample-projects"


def test_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "scs-scanner" in result.output


@pytest.mark.skipif(not (SAMPLE_PROJECTS / "python-vulnerable").exists(), reason="sample projects not available")
def test_scan_command_json(tmp_path):
    output = tmp_path / "report.json"
    result = runner.invoke(
        app,
        ["scan", str(SAMPLE_PROJECTS / "python-vulnerable"), "--format", "json", "--output", str(output)],
    )
    assert result.exit_code == 0
    assert output.exists()


@pytest.mark.skipif(not (SAMPLE_PROJECTS / "python-vulnerable").exists(), reason="sample projects not available")
def test_scan_fail_on_high(tmp_path):
    result = runner.invoke(
        app,
        ["scan", str(SAMPLE_PROJECTS / "python-vulnerable"), "--fail-on", "high"],
    )
    assert result.exit_code == 1


@pytest.mark.skipif(not (SAMPLE_PROJECTS / "python-secure").exists(), reason="sample projects not available")
def test_scan_secure_project_no_fail(tmp_path):
    result = runner.invoke(
        app,
        ["scan", str(SAMPLE_PROJECTS / "python-secure"), "--fail-on", "high"],
    )
    assert result.exit_code == 0


def test_scan_invalid_path():
    result = runner.invoke(app, ["scan", "/nonexistent/path/xyz"])
    assert result.exit_code == 1
