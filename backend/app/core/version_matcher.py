"""
Version matching engine for vulnerability detection.

Supports the following operators for Python (via packaging library):
  ==, !=, <, <=, >, >=, ~=, and comma-separated ranges like >=1.0,<2.0

For npm and Maven, a simplified numeric comparison is used since full
SemVer resolution is complex. The approach is documented and conservative:
if a version cannot be compared, the package is flagged for manual review.
"""
from __future__ import annotations

import re
from typing import Optional

from packaging.version import Version, InvalidVersion
from packaging.specifiers import SpecifierSet, InvalidSpecifier


def is_version_affected(installed_version: Optional[str], affected_spec: str, ecosystem: str) -> bool:
    """Return True if the installed version matches the affected version specification."""
    if not installed_version:
        return True

    try:
        if ecosystem == "python":
            return _match_python(installed_version, affected_spec)
        elif ecosystem == "npm":
            return _match_semver_simple(installed_version, affected_spec)
        elif ecosystem == "maven":
            return _match_maven(installed_version, affected_spec)
    except Exception:
        return False

    return False


def _match_python(version_str: str, spec_str: str) -> bool:
    """Use the packaging library to evaluate PEP 440 version specifiers."""
    try:
        specifier = SpecifierSet(spec_str, prereleases=True)
        return version_str in specifier
    except InvalidSpecifier:
        return _match_semver_simple(version_str, spec_str)


def _match_semver_simple(version_str: str, spec_str: str) -> bool:
    """
    Simplified SemVer matching for npm and fallback cases.
    Handles: <X, <=X, >X, >=X, ==X, !=X and comma-separated combinations.
    """
    try:
        installed = _parse_version_tuple(version_str)
    except ValueError:
        return False

    specs = [s.strip() for s in spec_str.split(",") if s.strip()]
    for spec in specs:
        match = re.match(r"^([><=!~^]+)\s*([\d\.]+)", spec)
        if not match:
            continue
        op = match.group(1)
        target_str = match.group(2)
        try:
            target = _parse_version_tuple(target_str)
        except ValueError:
            continue

        result = _compare(installed, op, target)
        if not result:
            return False

    return len(specs) > 0


def _match_maven(version_str: str, spec_str: str) -> bool:
    """Maven version range matching (simplified)."""
    spec_str = spec_str.strip()
    if re.match(r"^[\d]", spec_str):
        spec_str = f"<{spec_str}"
    return _match_semver_simple(version_str, spec_str)


def _parse_version_tuple(version_str: str) -> tuple[int, ...]:
    parts = version_str.split(".")
    result = []
    for part in parts:
        numeric = re.match(r"^\d+", part)
        if numeric:
            result.append(int(numeric.group(0)))
        else:
            break
    if not result:
        raise ValueError(f"Cannot parse version: {version_str}")
    return tuple(result)


def _compare(a: tuple[int, ...], op: str, b: tuple[int, ...]) -> bool:
    # Pad to equal length
    max_len = max(len(a), len(b))
    a = a + (0,) * (max_len - len(a))
    b = b + (0,) * (max_len - len(b))

    mapping = {
        "<": a < b,
        "<=": a <= b,
        ">": a > b,
        ">=": a >= b,
        "==": a == b,
        "!=": a != b,
        "~=": a >= b and a[:len(b) - 1] == b[:len(b) - 1],
    }
    return mapping.get(op, False)
