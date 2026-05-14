import json
import pytest
from pathlib import Path

from app.reporters.json_reporter import generate_json_report
from app.reporters.markdown_reporter import generate_markdown_report
from app.reporters.html_reporter import generate_html_report
from app.services.scan_service import run_scan


@pytest.fixture
def scan_result(fixtures_dir, tmp_path):
    import shutil
    shutil.copy(fixtures_dir / "requirements.txt", tmp_path / "requirements.txt")
    return run_scan(tmp_path)


def test_json_report_is_valid_json(scan_result):
    content = generate_json_report(scan_result)
    data = json.loads(content)
    assert "scan_id" in data
    assert "risk_score" in data
    assert "components" in data
    assert "vulnerabilities" in data


def test_json_report_to_file(scan_result, tmp_path):
    output = tmp_path / "report.json"
    generate_json_report(scan_result, output_path=output)
    assert output.exists()
    data = json.loads(output.read_text())
    assert "scan_id" in data


def test_markdown_report_contains_sections(scan_result):
    content = generate_markdown_report(scan_result)
    assert "# Supply Chain Security Report" in content
    assert "## Executive Summary" in content
    assert "## SBOM" in content
    assert "## Analysis Limits" in content


def test_markdown_report_to_file(scan_result, tmp_path):
    output = tmp_path / "report.md"
    generate_markdown_report(scan_result, output_path=output)
    assert output.exists()


def test_html_report_is_valid_html(scan_result):
    content = generate_html_report(scan_result)
    assert "<!DOCTYPE html>" in content
    assert "<title>" in content
    assert "Risk Score" in content


def test_html_report_to_file(scan_result, tmp_path):
    output = tmp_path / "report.html"
    generate_html_report(scan_result, output_path=output)
    assert output.exists()
