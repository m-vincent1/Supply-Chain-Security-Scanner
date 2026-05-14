# SBOM Format — Supply Chain Security Scanner

## Overview

This tool generates a **simplified SBOM** (Software Bill of Materials) inspired by the practices of software supply chain security. It is **not** a fully compliant CycloneDX or SPDX document.

If you need full CycloneDX or SPDX compliance, see the roadmap section.

## Format

```json
{
  "project_name": "my-project",
  "scan_date": "2026-05-14T10:30:00Z",
  "scanner_version": "1.0.0",
  "ecosystems": ["python", "npm"],
  "components": [
    {
      "name": "django",
      "version": "3.2.0",
      "ecosystem": "python",
      "source_file": "/path/to/requirements.txt",
      "dependency_type": "production"
    },
    {
      "name": "lodash",
      "version": "4.17.20",
      "ecosystem": "npm",
      "source_file": "/path/to/package.json",
      "dependency_type": "production"
    }
  ]
}
```

## Field descriptions

| Field | Type | Description |
|-------|------|-------------|
| `project_name` | string | Name of the scanned project |
| `scan_date` | ISO 8601 datetime | UTC timestamp of the scan |
| `scanner_version` | string | Version of the scanner that produced this SBOM |
| `ecosystems` | string[] | List of ecosystems detected in the project |
| `components` | array | List of all detected components |
| `components[].name` | string | Package name as declared in the manifest |
| `components[].version` | string or null | Resolved version, null if undetectable |
| `components[].ecosystem` | enum | `python`, `npm`, or `maven` |
| `components[].source_file` | string | Absolute path to the manifest file |
| `components[].dependency_type` | enum | `production`, `development`, `test`, or `unknown` |

## Relationship with CycloneDX and SPDX

This format is a subset of what CycloneDX and SPDX require. Key differences:

- No PURL (Package URL) identifiers
- No license information
- No hash/checksum per component
- No transitive dependency graph
- No supplier or author metadata

These features are listed in the project roadmap.

## Generating a SBOM

```bash
scs-scanner sbom ./my-project --output sbom.json
```

Or via the API:

```
GET /api/scans/{scan_id}/sbom
```
