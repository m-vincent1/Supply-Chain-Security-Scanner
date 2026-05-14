from app.models.schemas import (
    Component, DetectedVulnerability, DependencyType, Ecosystem, RiskLevel, Severity
)
from app.scoring.risk_scorer import compute_risk_score


def make_component(name="pkg", version="1.0.0", dep_type=DependencyType.production, pinned=True):
    return Component(
        name=name, version=version, ecosystem=Ecosystem.python,
        source_file="requirements.txt", dependency_type=dep_type, is_pinned=pinned,
    )


def make_vuln(package="pkg", severity=Severity.high, cvss=8.0):
    return DetectedVulnerability(
        vulnerability_id="DEMO-TEST-001",
        package=package, installed_version="1.0.0",
        ecosystem=Ecosystem.python,
        severity=severity, cvss=cvss,
        summary="Test vuln", recommendation="Upgrade",
        affected_versions="<2.0",
    )


def test_no_vulnerabilities_low_score():
    components = [make_component()]
    result = compute_risk_score(components, [])
    assert result.total == 0.0
    assert result.level == RiskLevel.low


def test_critical_vulnerability_raises_score():
    components = [make_component()]
    vulns = [make_vuln(severity=Severity.critical, cvss=9.8)]
    result = compute_risk_score(components, vulns)
    assert result.total > 20


def test_unpinned_penalty():
    components = [make_component(pinned=False) for _ in range(10)]
    result = compute_risk_score(components, [])
    assert result.total > 0


def test_dev_dependency_lower_score():
    prod = [make_component(dep_type=DependencyType.production)]
    dev = [make_component(dep_type=DependencyType.development)]
    vuln = [make_vuln(severity=Severity.high, cvss=8.0)]

    score_prod = compute_risk_score(prod, vuln)
    score_dev = compute_risk_score(dev, vuln)
    assert score_prod.total > score_dev.total


def test_multiple_vulns_same_package_increases_score():
    components = [make_component()]
    one_vuln = [make_vuln()]
    two_vulns = [make_vuln(), make_vuln(severity=Severity.medium, cvss=6.0)]

    score_one = compute_risk_score(components, one_vuln)
    score_two = compute_risk_score(components, two_vulns)
    assert score_two.total > score_one.total


def test_score_capped_at_100():
    components = [make_component() for _ in range(20)]
    vulns = [make_vuln(severity=Severity.critical, cvss=10.0) for _ in range(20)]
    result = compute_risk_score(components, vulns)
    assert result.total <= 100.0
