import React, { useEffect, useState } from 'react'
import { api } from '../api'
import type { VulnerabilityEntry, Severity } from '../types'
import SeverityBadge from '../components/SeverityBadge'
import './Dashboard.css'

const ECOSYSTEMS = ['', 'python', 'npm', 'maven']
const SEVERITIES = ['', 'critical', 'high', 'medium', 'low']

export default function Vulnerabilities() {
  const [vulns, setVulns] = useState<VulnerabilityEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [ecosystem, setEcosystem] = useState('')
  const [severity, setSeverity] = useState('')

  useEffect(() => {
    setLoading(true)
    api.listVulnerabilities(ecosystem || undefined, severity || undefined)
      .then(setVulns)
      .catch(() => setError('Unable to load vulnerabilities.'))
      .finally(() => setLoading(false))
  }, [ecosystem, severity])

  return (
    <div className="page">
      <h1 className="page-title">Vulnerability Database</h1>
      <div className="card">
        <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
          <select
            value={ecosystem}
            onChange={e => setEcosystem(e.target.value)}
            style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid var(--border)', fontSize: '0.9rem' }}
          >
            {ECOSYSTEMS.map(e => <option key={e} value={e}>{e || 'All ecosystems'}</option>)}
          </select>
          <select
            value={severity}
            onChange={e => setSeverity(e.target.value)}
            style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid var(--border)', fontSize: '0.9rem' }}
          >
            {SEVERITIES.map(s => <option key={s} value={s}>{s || 'All severities'}</option>)}
          </select>
          <span style={{ alignSelf: 'center', fontSize: '0.85rem', color: '#666' }}>
            {loading ? 'Loading...' : `${vulns.length} entries`}
          </span>
        </div>

        {error ? (
          <div className="page-error">{error}</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Package</th>
                <th>Ecosystem</th>
                <th>Severity</th>
                <th>CVSS</th>
                <th>Affected</th>
                <th>Summary</th>
                <th>Recommendation</th>
              </tr>
            </thead>
            <tbody>
              {vulns.map(v => (
                <tr key={v.id}>
                  <td style={{ fontSize: '0.78rem', color: '#666', whiteSpace: 'nowrap' }}>{v.id}</td>
                  <td><strong>{v.package}</strong></td>
                  <td>{v.ecosystem}</td>
                  <td><SeverityBadge severity={v.severity} size="sm" /></td>
                  <td>{v.cvss}</td>
                  <td style={{ fontSize: '0.82rem', whiteSpace: 'nowrap' }}>{v.affected_versions}</td>
                  <td style={{ fontSize: '0.85rem' }}>{v.summary.slice(0, 80)}</td>
                  <td style={{ fontSize: '0.82rem', color: '#3b82f6' }}>{v.recommendation.slice(0, 60)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
