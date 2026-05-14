import json
from pathlib import Path

from app.models.schemas import ScanResult


def generate_json_report(result: ScanResult, output_path: Path | None = None) -> str:
    data = result.model_dump(mode="json")
    content = json.dumps(data, indent=2, default=str)
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
    return content
