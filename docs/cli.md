# CLI Reference — scs-scanner

## Installation

```bash
pip install -e cli/.[dev]
```

## Commands

### scs-scanner scan

Scan a project for vulnerable dependencies.

```bash
scs-scanner scan PATH [OPTIONS]
```

Options:

| Option | Default | Description |
|--------|---------|-------------|
| `--format, -f` | terminal | Output format: `terminal`, `json`, `markdown`, `html` |
| `--output, -o` | stdout | Write report to file |
| `--fail-on` | none | Exit code 1 if vulnerabilities at or above this level exist |
| `--offline/--online` | offline | Use offline or online vulnerability database |
| `--include-dev/--exclude-dev` | include | Include development dependencies |
| `--verbose, -v` | false | Show full vulnerability table in terminal |

Examples:

```bash
# Basic terminal scan
scs-scanner scan ./my-project

# JSON report
scs-scanner scan ./my-project --format json --output reports/report.json

# Markdown report with verbose output
scs-scanner scan ./my-project --format markdown --output report.md --verbose

# HTML report
scs-scanner scan ./my-project --format html --output report.html

# CI/CD gate — fail if high or above
scs-scanner scan . --fail-on high

# Exclude dev dependencies from analysis
scs-scanner scan . --exclude-dev --fail-on critical

# Scan sample projects
scs-scanner scan sample-projects/python-vulnerable --format markdown
scs-scanner scan sample-projects/node-vulnerable --format json
```

### scs-scanner sbom

Generate a simplified SBOM.

```bash
scs-scanner sbom PATH --output sbom.json
```

### scs-scanner validate

Check if a project contains supported dependency files.

```bash
scs-scanner validate ./my-project
```

### scs-scanner version

Print the scanner version.

```bash
scs-scanner version
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Scan completed successfully, no gate triggered |
| 1 | Error, or `--fail-on` gate triggered |
