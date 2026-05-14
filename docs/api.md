# API Reference — Supply Chain Security Scanner

Base URL: `http://localhost:8000`

Interactive documentation: `http://localhost:8000/docs`

---

## GET /health

Health check endpoint.

Response:
```json
{ "status": "ok", "service": "Supply Chain Security Scanner", "version": "1.0.0" }
```

---

## GET /version

Returns the scanner version.

```json
{ "version": "1.0.0" }
```

---

## POST /api/scans

Trigger a new scan.

Request body:
```json
{
  "project_path": "/sample-projects/python-vulnerable",
  "project_name": "my-project",
  "include_dev": true,
  "offline": true
}
```

Response (201):
```json
{
  "scan_id": "uuid",
  "project_name": "python-vulnerable",
  "scan_date": "2026-05-14T10:30:00Z",
  "risk_score": 82.0,
  "risk_level": "Critical",
  "status": "completed",
  "total_dependencies": 9,
  "total_vulnerabilities": 7,
  "vulnerabilities_by_severity": { "critical": 2, "high": 3, "medium": 2, "low": 0 },
  "ecosystems": ["python"]
}
```

---

## GET /api/scans

List all scans (paginated).

Query params: `limit` (default 50), `offset` (default 0)

---

## GET /api/scans/{scan_id}

Get full scan result including all vulnerabilities, remediations, SBOM, and components.

---

## GET /api/scans/{scan_id}/sbom

Get the simplified SBOM for a scan.

---

## GET /api/scans/{scan_id}/report

Get a formatted report for a scan.

Query param: `format` = `json` | `markdown` | `html`

Response: `{ "content": "..." }`

---

## GET /api/vulnerabilities

List all entries in the vulnerability database.

Query params: `ecosystem` (optional), `severity` (optional)
