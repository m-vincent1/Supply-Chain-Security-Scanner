# DevSecOps Integration Guide

## Using the scanner in CI/CD pipelines

The `--fail-on` flag makes the CLI usable as a quality gate. If vulnerabilities at or above the specified severity are found, the command exits with code 1, which causes the pipeline to fail.

```bash
scs-scanner scan . --fail-on high
```

## GitHub Actions example

```yaml
name: Supply Chain Security Scan

on:
  push:
    branches: [main]
  pull_request:

jobs:
  security-scan:
    name: Dependency vulnerability scan
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install scs-scanner
        run: |
          pip install -e backend/.[dev]
          pip install -e cli/.[dev]

      - name: Scan dependencies
        run: |
          scs-scanner scan . --format json --output reports/scan.json --fail-on high

      - name: Upload security report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: security-report
          path: reports/scan.json
```

## Blocking a pipeline on critical findings only

```yaml
- name: Block on critical vulnerabilities
  run: scs-scanner scan . --fail-on critical --exclude-dev
```

## Generating a report without failing the pipeline

```yaml
- name: Generate security report
  run: scs-scanner scan . --format html --output reports/security.html
  continue-on-error: true
```

## Recommended severity gates by environment

| Environment | Recommended gate |
|-------------|-----------------|
| Development branch | `--fail-on critical` |
| Staging / release branch | `--fail-on high` |
| Production main branch | `--fail-on medium` |

## Best practices

1. Run the scan on every pull request, not just on merges to main.
2. Pin all production dependencies. Unpinned dependencies increase risk score and break reproducibility.
3. Keep the vulnerability database up to date (roadmap: OSV live integration).
4. Treat the SBOM output as an artifact — archive it alongside your build artifacts.
5. Review the `--include-dev / --exclude-dev` flag. Development dependencies are often not deployed, but can still introduce risk via build chains.

## GitLab CI example

```yaml
security-scan:
  image: python:3.11
  stage: test
  script:
    - pip install -e backend/.[dev] cli/.[dev]
    - scs-scanner scan . --fail-on high --format json --output gl-dependency-scanning-report.json
  artifacts:
    paths:
      - gl-dependency-scanning-report.json
    when: always
```
