import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api'
import type { ScanResult } from '../types'
import SeverityBadge from '../components/SeverityBadge'
import ScoreGauge from '../components/ScoreGauge'
import './Dashboard.css'
import './ScanDetail.css'

export default function ScanDetail() {
  const { id } = useParams<{ id: string }>()
  const [scan, setScan] = useState<ScanResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    api.getScan(id)
      .then(setScan)
      .catch(() => setError('Scan not found or API unavailable.'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="page-loading">Loading scan...</div>
  if (error || !scan) return <div className="page-error">{error}</div>

  const sv = scan.vulnerabilities_by_severity

  return (
    <div className="page">
      <div style={{ marginBottom: 16 }}>
        <Link to="/scans" className="btn-link" style={{ fontSize: '0.85rem' }}>Back to scans</Link>
      </div>

      <div className="scan-header">
        <div>
          <h1 className="page-title">{scan.project_name}</h1>
          <p style={{ color: '#666', fontSize: '0.9rem' }}>
            Scanned on {new Date(scan.scan_date).toLocaleString()} — Scanner v{scan.scanner_version}
          </p>
        </div>
        <ScoreGauge score={scan.risk_score.total} level={scan.risk_score.level} size={90} />
      </div>

      <div className="stat-grid">
        {[
          { label: 'Dependencies', value: scan.total_dependencies, color: '#3b82f6' },
          { label: 'Vulnerabilities', value: scan.total_vulnerabilities, color: scan.total_vulnerabilities > 0 ? '#c0392b' : '#276749' },
          { label: 'Critical', value: sv.critical || 0, color: '#c0392b' },
          { label: 'High', value: sv.high || 0, color: '#d35400' },
          { label: 'Medium', value: sv.medium || 0, color: '#b7791f' },
          { label: 'Low', value: sv.low || 0, color: '#276749' },
        ].map(s => (
          <div className="stat-card" key={s.label}>
            <div className="stat-label">{s.label}</div>
            <div className="stat-value" style={{ color: s.color }}>{s.value}</div>
          </div>
        ))}
      </div>

      {scan.vulnerabilities.length > 0 && (
        <div className="card">
          <h2 className="card-title">Detected vulnerabilities</h2>
          <table className="data-table">
            <thead>
              <tr>
                <th>Package</th><th>Version</th><th>Severity</th><th>CVSS</th><th>ID</th><th>Summary</th>
              </tr>
            </thead>
            <tbody>
              {[...scan.vulnerabilities].sort((a, b) => b.cvss - a.cvss).map((v, i) => (
                <tr key={i}>
                  <td><strong>{v.package}</strong></td>
                  <td>{v.installed_version || 'unknown'}</td>
                  <td><SeverityBadge severity={v.severity} size="sm" /></td>
                  <td>{v.cvss}</td>
                  <td style={{ fontSize: '0.78rem', color: '#666' }}>{v.vulnerability_id}</td>
                  <td style={{ fontSize: '0.85rem' }}>{v.summary.slice(0, 90)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {scan.remediations.length > 0 && (
        <div className="card">
          <h2 className="card-title">Remediation recommendations</h2>
          <div className="rem-list">
            {scan.remediations.map((rem, i) => (
              <div className="rem-item" key={i}>
                <div className="rem-header">
                  <strong>{rem.package}</strong>
                  <SeverityBadge severity={rem.priority} size="sm" />
                </div>
                <div className="rem-row"><span>Risk</span><span>{rem.risk}</span></div>
                <div className="rem-row"><span>Evidence</span><span>{rem.evidence}</span></div>
                <div className="rem-row"><span>Action</span><span>{rem.action}</span></div>
                {rem.suggested_command && (
                  <div className="rem-cmd"><code>{rem.suggested_command}</code></div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card">
        <h2 className="card-title">SBOM — Software Bill of Materials</h2>
        <table className="data-table">
          <thead>
            <tr><th>Package</th><th>Version</th><th>Ecosystem</th><th>Type</th><th>Pinned</th></tr>
          </thead>
          <tbody>
            {scan.sbom.components.map((c, i) => (
              <tr key={i}>
                <td>{c.name}</td>
                <td>{c.version || '-'}</td>
                <td>{c.ecosystem}</td>
                <td>{c.dependency_type}</td>
                <td>{scan.components.find(x => x.name === c.name)?.is_pinned ? 'Yes' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h2 className="card-title">Analysis limits</h2>
        <ul style={{ paddingLeft: 20 }}>
          {scan.analysis_limits.map((l, i) => (
            <li key={i} style={{ marginBottom: 4, fontSize: '0.9rem', color: '#666' }}>{l}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}
