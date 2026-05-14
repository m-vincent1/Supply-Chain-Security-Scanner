from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.models.schemas import (
    SBOM,
    SBOMComponent,
    ScanResult,
    ScanStatus,
    ScanSummary,
)
from app.parsers import detect_and_parse
from app.scoring.risk_scorer import compute_risk_score
from app.services.vulnerability_service import VulnerabilityService


_vuln_service = VulnerabilityService()


def run_scan(
    project_path: Path,
    project_name: str | None = None,
    include_dev: bool = True,
    offline: bool = True,
) -> ScanResult:
    if not project_path.exists():
        raise FileNotFoundError(f"Project path does not exist: {project_path}")

    scan_id = str(uuid.uuid4())
    scan_date = datetime.now(timezone.utc)
    name = project_name or project_path.name

    components = detect_and_parse(project_path)

    vulnerabilities, remediations = _vuln_service.scan_components(components, include_dev=include_dev)

    risk_score = compute_risk_score(components, vulnerabilities)

    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for v in vulnerabilities:
        key = v.severity.value
        severity_counts[key] = severity_counts.get(key, 0) + 1

    ecosystems = sorted({c.ecosystem.value for c in components})

    sbom = SBOM(
        project_name=name,
        scan_date=scan_date,
        scanner_version=settings.app_version,
        ecosystems=ecosystems,
        components=[
            SBOMComponent(
                name=c.name,
                version=c.version,
                ecosystem=c.ecosystem,
                source_file=c.source_file,
                dependency_type=c.dependency_type,
            )
            for c in components
        ],
    )

    limits = _build_analysis_limits(components)

    return ScanResult(
        scan_id=scan_id,
        project_name=name,
        scanned_path=str(project_path.resolve()),
        scan_date=scan_date,
        scanner_version=settings.app_version,
        total_dependencies=len(components),
        total_vulnerabilities=len(vulnerabilities),
        vulnerabilities_by_severity=severity_counts,
        risk_score=risk_score,
        components=components,
        vulnerabilities=vulnerabilities,
        remediations=remediations,
        sbom=sbom,
        ecosystems=ecosystems,
        analysis_limits=limits,
    )


def result_to_summary(result: ScanResult, status: ScanStatus = ScanStatus.completed) -> ScanSummary:
    return ScanSummary(
        scan_id=result.scan_id,
        project_name=result.project_name,
        scan_date=result.scan_date,
        risk_score=result.risk_score.total,
        risk_level=result.risk_score.level,
        status=status,
        total_dependencies=result.total_dependencies,
        total_vulnerabilities=result.total_vulnerabilities,
        vulnerabilities_by_severity=result.vulnerabilities_by_severity,
        ecosystems=result.ecosystems,
    )


def _build_analysis_limits(components) -> list[str]:
    limits = [
        "Vulnerability database is a demonstration dataset, not a live feed.",
        "Version matching uses simplified heuristics for npm and Maven ecosystems.",
        "License analysis is not included in this version.",
        "Transitive dependencies are not resolved.",
    ]
    if not components:
        limits.append("No supported dependency files were found in the project path.")
    return limits
