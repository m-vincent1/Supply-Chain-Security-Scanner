from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class Ecosystem(str, Enum):
    python = "python"
    npm = "npm"
    maven = "maven"


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class RiskLevel(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class DependencyType(str, Enum):
    production = "production"
    development = "development"
    test = "test"
    unknown = "unknown"


class ScanStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class Component(BaseModel):
    name: str
    version: Optional[str] = None
    ecosystem: Ecosystem
    source_file: str
    dependency_type: DependencyType = DependencyType.unknown
    line_number: Optional[int] = None
    is_pinned: bool = True


class VulnType(str, Enum):
    cve = "cve"
    supply_chain_attack = "supply_chain_attack"
    abandoned = "abandoned"
    typosquatting = "typosquatting"


class RemediationType(str, Enum):
    upgrade = "upgrade"
    remove = "remove"
    migrate = "migrate"
    pin_safe_version = "pin_safe_version"


VULN_TYPE_LABELS: dict[str, str] = {
    "cve": "CVE",
    "supply_chain_attack": "Supply Chain Attack",
    "abandoned": "Abandoned Package",
    "typosquatting": "Typosquatting",
}

REMEDIATION_TYPE_LABELS: dict[str, str] = {
    "upgrade": "Upgrade",
    "remove": "Remove immediately",
    "migrate": "Migrate to alternative",
    "pin_safe_version": "Pin safe version",
}


class VulnerabilityEntry(BaseModel):
    id: str
    package: str
    ecosystem: Ecosystem
    affected_versions: str
    severity: Severity
    cvss: float
    vuln_type: VulnType = VulnType.cve
    remediation_type: RemediationType = RemediationType.upgrade
    summary: str
    recommendation: str
    references: list[str] = Field(default_factory=list)


class DetectedVulnerability(BaseModel):
    vulnerability_id: str
    package: str
    installed_version: Optional[str]
    ecosystem: Ecosystem
    severity: Severity
    cvss: float
    vuln_type: VulnType = VulnType.cve
    remediation_type: RemediationType = RemediationType.upgrade
    summary: str
    recommendation: str
    affected_versions: str
    references: list[str] = Field(default_factory=list)


class Remediation(BaseModel):
    package: str
    ecosystem: Ecosystem
    risk: str
    impact: str
    evidence: str
    action: str
    suggested_command: Optional[str]
    priority: Severity


class RiskScore(BaseModel):
    total: float
    level: RiskLevel
    breakdown: dict[str, float] = Field(default_factory=dict)


class SBOMComponent(BaseModel):
    name: str
    version: Optional[str]
    ecosystem: Ecosystem
    source_file: str
    dependency_type: DependencyType


class SBOM(BaseModel):
    project_name: str
    scan_date: datetime
    scanner_version: str
    ecosystems: list[str]
    components: list[SBOMComponent]


class ScanResult(BaseModel):
    scan_id: str
    project_name: str
    scanned_path: str
    scan_date: datetime
    scanner_version: str
    total_dependencies: int
    total_vulnerabilities: int
    vulnerabilities_by_severity: dict[str, int]
    risk_score: RiskScore
    components: list[Component]
    vulnerabilities: list[DetectedVulnerability]
    remediations: list[Remediation]
    sbom: SBOM
    ecosystems: list[str]
    analysis_limits: list[str] = Field(default_factory=list)


class ScanRequest(BaseModel):
    project_path: str
    project_name: Optional[str] = None
    include_dev: bool = True
    offline: bool = True


class ScanSummary(BaseModel):
    scan_id: str
    project_name: str
    scan_date: datetime
    risk_score: float
    risk_level: RiskLevel
    status: ScanStatus
    total_dependencies: int
    total_vulnerabilities: int
    vulnerabilities_by_severity: dict[str, int]
    ecosystems: list[str]
