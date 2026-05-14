from pathlib import Path
from typing import Literal

from app.models.schemas import ScanResult
from app.reporters.json_reporter import generate_json_report
from app.reporters.markdown_reporter import generate_markdown_report
from app.reporters.html_reporter import generate_html_report

ReportFormat = Literal["json", "markdown", "html"]


def generate_report(
    result: ScanResult,
    fmt: ReportFormat = "json",
    output_path: Path | None = None,
) -> str:
    if fmt == "json":
        return generate_json_report(result, output_path)
    elif fmt == "markdown":
        return generate_markdown_report(result, output_path)
    elif fmt == "html":
        return generate_html_report(result, output_path)
    raise ValueError(f"Unsupported report format: {fmt}")
