"""
Risk scoring engine.

Formula documented in docs/risk-scoring.md.

Score is computed on a 0-100 scale from:
  - Vulnerability severity and CVSS scores (base component)
  - Production vs. development scope multiplier
  - Unpinned dependencies penalty
  - Multiple vulnerabilities on the same package
"""
from __future__ import annotations

from collections import Counter

from app.models.schemas import (
    Component,
    DetectedVulnerability,
    DependencyType,
    RiskLevel,
    RiskScore,
    Severity,
)

SEVERITY_WEIGHTS: dict[str, float] = {
    Severity.critical.value: 40.0,
    Severity.high.value: 20.0,
    Severity.medium.value: 10.0,
    Severity.low.value: 4.0,
}

SCOPE_MULTIPLIER: dict[str, float] = {
    DependencyType.production.value: 1.0,
    DependencyType.development.value: 0.5,
    DependencyType.test.value: 0.3,
    DependencyType.unknown.value: 0.8,
}

UNPINNED_PENALTY_PER_DEP = 1.5
MAX_RAW_SCORE = 150.0


def compute_risk_score(
    components: list[Component],
    vulnerabilities: list[DetectedVulnerability],
) -> RiskScore:
    raw = 0.0
    breakdown: dict[str, float] = {
        "vulnerability_score": 0.0,
        "unpinned_penalty": 0.0,
    }

    component_map = {c.name.lower(): c for c in components}
    vuln_counts: Counter[str] = Counter(v.package.lower() for v in vulnerabilities)

    for vuln in vulnerabilities:
        base = SEVERITY_WEIGHTS.get(vuln.severity.value, 5.0)
        cvss_multiplier = (vuln.cvss / 10.0) if vuln.cvss else 0.5
        component = component_map.get(vuln.package.lower())
        scope_mult = SCOPE_MULTIPLIER.get(
            component.dependency_type.value if component else DependencyType.unknown.value,
            0.8,
        )
        repeat_factor = 1.0 + 0.1 * (vuln_counts[vuln.package.lower()] - 1)
        contribution = base * cvss_multiplier * scope_mult * repeat_factor
        raw += contribution
        breakdown["vulnerability_score"] += contribution

    unpinned = sum(1 for c in components if not c.is_pinned and c.dependency_type != DependencyType.development)
    unpinned_penalty = unpinned * UNPINNED_PENALTY_PER_DEP
    raw += unpinned_penalty
    breakdown["unpinned_penalty"] = unpinned_penalty

    normalized = min(100.0, (raw / MAX_RAW_SCORE) * 100.0)
    total = round(normalized, 1)

    return RiskScore(
        total=total,
        level=_score_to_level(total),
        breakdown={k: round(v, 2) for k, v in breakdown.items()},
    )


def _score_to_level(score: float) -> RiskLevel:
    if score <= 20:
        return RiskLevel.low
    if score <= 50:
        return RiskLevel.medium
    if score <= 75:
        return RiskLevel.high
    return RiskLevel.critical
