import pytest
from app.core.version_matcher import is_version_affected


@pytest.mark.parametrize("version,spec,ecosystem,expected", [
    # Python exact and range
    ("3.2.0", "<3.2.20", "python", True),
    ("3.2.20", "<3.2.20", "python", False),
    ("3.2.21", "<3.2.20", "python", False),
    ("1.0.0", ">=1.0,<2.0", "python", True),
    ("2.0.0", ">=1.0,<2.0", "python", False),
    ("3.2.0", "==3.2.0", "python", True),
    ("3.2.1", "==3.2.0", "python", False),
    # npm simplified
    ("4.17.20", "<4.17.21", "npm", True),
    ("4.17.21", "<4.17.21", "npm", False),
    ("4.17.22", "<4.17.21", "npm", False),
    # maven simplified
    ("2.14.0", "<2.17.1", "maven", True),
    ("2.17.1", "<2.17.1", "maven", False),
    ("2.17.2", "<2.17.1", "maven", False),
    # missing version
    (None, "<1.0.0", "python", True),
])
def test_version_matching(version, spec, ecosystem, expected):
    assert is_version_affected(version, spec, ecosystem) == expected


def test_greater_than_equal():
    assert is_version_affected("2.0.0", ">=2.0.0", "python") is True
    assert is_version_affected("1.9.9", ">=2.0.0", "python") is False


def test_not_equal():
    assert is_version_affected("1.0.0", "!=1.0.0", "python") is False
    assert is_version_affected("1.0.1", "!=1.0.0", "python") is True
