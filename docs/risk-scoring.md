# Risk Scoring — Supply Chain Security Scanner

## Overview

The risk scorer produces a score between 0 and 100. This score is intended to be transparent, reproducible, and testable. It does not claim mathematical precision — it is an opinionated heuristic designed to surface the most dangerous dependencies first.

## Score levels

| Range | Level    |
|-------|----------|
| 0-20  | Low      |
| 21-50 | Medium   |
| 51-75 | High     |
| 76-100| Critical |

## Formula

```
raw_score = sum over all vulnerabilities of:
    base_weight(severity) * cvss_multiplier * scope_multiplier * repeat_factor

raw_score += unpinned_count * UNPINNED_PENALTY

normalized_score = min(100, raw_score / MAX_RAW_SCORE * 100)
```

### Base weights by severity

| Severity | Weight |
|----------|--------|
| critical | 40.0   |
| high     | 20.0   |
| medium   | 10.0   |
| low      | 4.0    |

### CVSS multiplier

`cvss_multiplier = cvss / 10.0`

A CVSS 9.8 vulnerability weights 98% of the base; a CVSS 3.0 weights 30%.

### Scope multiplier

| Dependency type | Multiplier |
|-----------------|------------|
| production      | 1.0        |
| unknown         | 0.8        |
| development     | 0.5        |
| test            | 0.3        |

Development dependencies are not exploitable in production, so their weight is reduced.

### Repeat factor

If a package has N vulnerabilities, each vulnerability gets a `repeat_factor = 1.0 + 0.1 * (N - 1)`.

A package with 3 vulnerabilities has a 20% amplification on each finding, reflecting that heavily vulnerable packages carry compounding risk.

### Unpinned dependency penalty

Each production dependency without a pinned version adds 1.5 points to the raw score.

Unpinned dependencies (`flask>=1.0`, `lodash: *`) introduce supply chain risk because the installed version is non-deterministic.

### Normalization

The raw score is normalized against `MAX_RAW_SCORE = 200.0`. This means that a project with a fully critical attack surface (many critical vulnerabilities, no pinning) will approach 100, while most real projects will fall in a meaningful range.

## Limitations

- The formula does not account for exploitability or whether a vulnerability is reachable in the specific code paths.
- License risk is not included in this version.
- Transitive dependencies are not resolved — only direct dependencies declared in supported files are analyzed.
- The vulnerability database is a demonstration dataset. Scores are for illustration only and should not be used for production compliance decisions.

## Implementation

See `backend/app/scoring/risk_scorer.py`.
