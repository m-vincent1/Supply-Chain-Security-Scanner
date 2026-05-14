from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import ScanRecord, get_db
from app.models.schemas import ScanRequest, ScanResult, ScanSummary, VulnerabilityEntry
from app.reporters import generate_report
from app.services.scan_service import result_to_summary, run_scan
from app.services.vulnerability_service import VulnerabilityService

router = APIRouter()
_vuln_service = VulnerabilityService()


@router.post("/scans", response_model=ScanSummary, status_code=201)
def create_scan(request: ScanRequest, db: Session = Depends(get_db)):
    project_path = Path(request.project_path)
    if not project_path.exists():
        raise HTTPException(status_code=400, detail=f"Path not found: {request.project_path}")

    try:
        result = run_scan(
            project_path=project_path,
            project_name=request.project_name,
            include_dev=request.include_dev,
            offline=request.offline,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    record = ScanRecord(
        id=result.scan_id,
        project_name=result.project_name,
        scanned_path=result.scanned_path,
        scan_date=result.scan_date,
        status="completed",
        total_dependencies=result.total_dependencies,
        total_vulnerabilities=result.total_vulnerabilities,
        risk_score=result.risk_score.total,
        risk_level=result.risk_score.level.value,
        ecosystems=result.ecosystems,
        vulnerabilities_by_severity=result.vulnerabilities_by_severity,
        result_json=result.model_dump_json(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return result_to_summary(result)


@router.get("/scans", response_model=list[ScanSummary])
def list_scans(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    records = db.query(ScanRecord).order_by(ScanRecord.scan_date.desc()).offset(offset).limit(limit).all()
    return [_record_to_summary(r) for r in records]


@router.get("/scans/{scan_id}", response_model=ScanResult)
def get_scan(scan_id: str, db: Session = Depends(get_db)):
    record = db.query(ScanRecord).filter(ScanRecord.id == scan_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Scan not found")
    if not record.result_json:
        raise HTTPException(status_code=404, detail="Scan result data not available")
    return ScanResult.model_validate_json(record.result_json)


@router.get("/scans/{scan_id}/sbom")
def get_scan_sbom(scan_id: str, db: Session = Depends(get_db)):
    record = db.query(ScanRecord).filter(ScanRecord.id == scan_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Scan not found")
    result = ScanResult.model_validate_json(record.result_json)
    return result.sbom


@router.get("/scans/{scan_id}/report")
def get_scan_report(
    scan_id: str,
    fmt: str = Query("json", alias="format"),
    db: Session = Depends(get_db),
):
    record = db.query(ScanRecord).filter(ScanRecord.id == scan_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Scan not found")
    result = ScanResult.model_validate_json(record.result_json)
    if fmt not in ("json", "markdown", "html"):
        raise HTTPException(status_code=400, detail="format must be json, markdown or html")
    return {"content": generate_report(result, fmt=fmt)}


@router.get("/vulnerabilities", response_model=list[VulnerabilityEntry])
def list_vulnerabilities(
    ecosystem: Optional[str] = None,
    severity: Optional[str] = None,
):
    vulns = _vuln_service.get_all_vulnerabilities()
    if ecosystem:
        vulns = [v for v in vulns if v.ecosystem.value == ecosystem]
    if severity:
        vulns = [v for v in vulns if v.severity.value == severity]
    return vulns


def _record_to_summary(record: ScanRecord) -> ScanSummary:
    from app.models.schemas import RiskLevel, ScanStatus
    from datetime import datetime

    return ScanSummary(
        scan_id=record.id,
        project_name=record.project_name,
        scan_date=record.scan_date if isinstance(record.scan_date, datetime) else datetime.fromisoformat(str(record.scan_date)),
        risk_score=record.risk_score or 0.0,
        risk_level=RiskLevel(record.risk_level) if record.risk_level else RiskLevel.low,
        status=ScanStatus(record.status) if record.status else ScanStatus.completed,
        total_dependencies=record.total_dependencies or 0,
        total_vulnerabilities=record.total_vulnerabilities or 0,
        vulnerabilities_by_severity=record.vulnerabilities_by_severity or {},
        ecosystems=record.ecosystems or [],
    )
