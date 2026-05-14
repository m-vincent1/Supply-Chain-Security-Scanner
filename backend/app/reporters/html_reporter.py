from pathlib import Path

from jinja2 import Environment, BaseLoader

from app.models.schemas import ScanResult

_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Security Report — {{ result.project_name }}</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #f5f7fa; color: #222; }
  .container { max-width: 1100px; margin: 0 auto; padding: 32px 24px; }
  h1 { font-size: 1.8rem; font-weight: 700; margin-bottom: 4px; }
  h2 { font-size: 1.2rem; font-weight: 600; margin-top: 32px; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; }
  .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; }
  .badge-critical { background: #fde8e8; color: #c0392b; }
  .badge-high { background: #fef3e0; color: #d35400; }
  .badge-medium { background: #fff8e1; color: #b7791f; }
  .badge-low { background: #e6f4ea; color: #276749; }
  .score-box { display: inline-block; padding: 12px 28px; border-radius: 8px; font-size: 2rem; font-weight: 700; margin: 16px 0; }
  .score-critical { background: #fde8e8; color: #c0392b; }
  .score-high { background: #fef3e0; color: #d35400; }
  .score-medium { background: #fff8e1; color: #b7791f; }
  .score-low { background: #e6f4ea; color: #276749; }
  table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
  th { background: #f1f5f9; text-align: left; padding: 8px 12px; }
  td { padding: 8px 12px; border-bottom: 1px solid #e2e8f0; }
  tr:hover td { background: #f8fafc; }
  .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin: 16px 0; }
  .stat-card { background: white; border-radius: 8px; padding: 16px; border: 1px solid #e2e8f0; }
  .stat-card .label { font-size: 0.8rem; color: #666; text-transform: uppercase; letter-spacing: 0.05em; }
  .stat-card .value { font-size: 1.6rem; font-weight: 700; margin-top: 4px; }
  .rem-block { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 12px; }
  .rem-block h4 { margin: 0 0 8px 0; }
  code { background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 0.85rem; }
  .limits { background: #fffbeb; border: 1px solid #fcd34d; border-radius: 6px; padding: 12px 16px; }
  .limits li { margin: 4px 0; font-size: 0.9rem; }
  footer { margin-top: 48px; font-size: 0.8rem; color: #888; text-align: center; }
</style>
</head>
<body>
<div class="container">
  <h1>Supply Chain Security Report</h1>
  <p style="color:#666;">Project: <strong>{{ result.project_name }}</strong> &mdash; {{ result.scan_date.strftime('%Y-%m-%d %H:%M UTC') }}</p>

  <div class="summary-grid">
    <div class="stat-card">
      <div class="label">Risk Score</div>
      <div class="value score-box score-{{ result.risk_score.level.value.lower() }}">{{ result.risk_score.total }}/100</div>
      <div>{{ result.risk_score.level.value }}</div>
    </div>
    <div class="stat-card">
      <div class="label">Dependencies</div>
      <div class="value">{{ result.total_dependencies }}</div>
    </div>
    <div class="stat-card">
      <div class="label">Vulnerabilities</div>
      <div class="value">{{ result.total_vulnerabilities }}</div>
    </div>
    <div class="stat-card">
      <div class="label">Critical</div>
      <div class="value" style="color:#c0392b;">{{ result.vulnerabilities_by_severity.get('critical', 0) }}</div>
    </div>
    <div class="stat-card">
      <div class="label">High</div>
      <div class="value" style="color:#d35400;">{{ result.vulnerabilities_by_severity.get('high', 0) }}</div>
    </div>
    <div class="stat-card">
      <div class="label">Medium</div>
      <div class="value" style="color:#b7791f;">{{ result.vulnerabilities_by_severity.get('medium', 0) }}</div>
    </div>
  </div>

  {% if result.vulnerabilities %}
  <h2>Detected Vulnerabilities</h2>
  <table>
    <thead><tr><th>Package</th><th>Version</th><th>Severity</th><th>CVSS</th><th>Type</th><th>ID</th><th>Summary</th></tr></thead>
    <tbody>
    {% set type_labels = {"cve": "CVE", "supply_chain_attack": "Supply Chain Attack", "abandoned": "Abandoned", "typosquatting": "Typosquatting"} %}
    {% set type_colors = {"cve": "#3b82f6", "supply_chain_attack": "#7c3aed", "abandoned": "#64748b", "typosquatting": "#b45309"} %}
    {% for v in result.vulnerabilities | sort(attribute='cvss', reverse=True) %}
    {% set vt = v.vuln_type.value if v.vuln_type else 'cve' %}
    <tr>
      <td><strong>{{ v.package }}</strong></td>
      <td>{{ v.installed_version or 'unknown' }}</td>
      <td><span class="badge badge-{{ v.severity.value }}">{{ v.severity.value.upper() }}</span></td>
      <td>{{ v.cvss }}</td>
      <td><span style="font-size:0.78rem;font-weight:600;color:{{ type_colors.get(vt, '#333') }};">{{ type_labels.get(vt, vt) }}</span></td>
      <td style="font-size:0.8rem;">{{ v.vulnerability_id }}</td>
      <td style="font-size:0.85rem;">{{ v.summary[:100] }}</td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
  {% endif %}

  {% if result.remediations %}
  <h2>Remediation Recommendations</h2>
  {% for rem in result.remediations %}
  <div class="rem-block">
    <h4>{{ rem.package }} <span class="badge badge-{{ rem.priority.value }}">{{ rem.priority.value.upper() }}</span></h4>
    <p><strong>Risk:</strong> {{ rem.risk }}</p>
    <p><strong>Evidence:</strong> {{ rem.evidence }}</p>
    <p><strong>Action:</strong> {{ rem.action }}</p>
    {% if rem.suggested_command %}
    <p><strong>Command:</strong> <code>{{ rem.suggested_command }}</code></p>
    {% endif %}
  </div>
  {% endfor %}
  {% endif %}

  <h2>SBOM — Software Bill of Materials</h2>
  <table>
    <thead><tr><th>Package</th><th>Version</th><th>Ecosystem</th><th>Type</th><th>Source</th></tr></thead>
    <tbody>
    {% for c in result.sbom.components %}
    <tr>
      <td>{{ c.name }}</td>
      <td>{{ c.version or '-' }}</td>
      <td>{{ c.ecosystem.value }}</td>
      <td>{{ c.dependency_type.value }}</td>
      <td style="font-size:0.8rem;color:#666;">{{ c.source_file | replace('\\\\', '/') | truncate(60, True, '...', 0) }}</td>
    </tr>
    {% endfor %}
    </tbody>
  </table>

  <h2>Analysis Limits</h2>
  <div class="limits">
    <ul>
    {% for limit in result.analysis_limits %}
      <li>{{ limit }}</li>
    {% endfor %}
    </ul>
  </div>

  <footer>Generated by Supply Chain Security Scanner v{{ result.scanner_version }} &mdash; {{ result.scan_date.strftime('%Y-%m-%d') }}</footer>
</div>
</body>
</html>
"""


def generate_html_report(result: ScanResult, output_path: Path | None = None) -> str:
    env = Environment(loader=BaseLoader())
    template = env.from_string(_TEMPLATE)
    content = template.render(result=result)
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
    return content
