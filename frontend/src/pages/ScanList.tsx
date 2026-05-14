import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import type { ScanSummary } from '../types'
import SeverityBadge from '../components/SeverityBadge'
import './Dashboard.css'

export default function ScanList() {
  const [scans, setScans] = useState<ScanSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.listScans()
      .then(setScans)
      .catch(() => setError('Unable to load scans.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="page-loading">Loading...</div>
  if (error) return <div className="page-error">{error}</div>

  return (
    <div className="page">
      <h1 className="page-title">Scans</h1>
      <div className="card">
        {scans.length === 0 ? (
          <div className="empty-state">
            No scans yet. Run <code>scs-scanner scan &lt;path&gt;</code> or POST to <code>/api/scans</code>.
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Project</th>
                <th>Date</th>
                <th>Score</th>
                <th>Level</th>
                <th>Dependencies</th>
                <th>Vulnerabilities</th>
                <th>Ecosystems</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {scans.map(scan => (
                <tr key={scan.scan_id}>
                  <td><strong>{scan.project_name}</strong></td>
                  <td>{new Date(scan.scan_date).toLocaleString()}</td>
                  <td>{scan.risk_score}/100</td>
                  <td><SeverityBadge severity={scan.risk_level.toLowerCase() as any} size="sm" /></td>
                  <td>{scan.total_dependencies}</td>
                  <td>
                    {scan.total_vulnerabilities > 0 ? (
                      <span style={{ color: '#c0392b', fontWeight: 600 }}>{scan.total_vulnerabilities}</span>
                    ) : (
                      <span style={{ color: '#276749' }}>0</span>
                    )}
                  </td>
                  <td style={{ fontSize: '0.82rem', color: '#666' }}>
                    {scan.ecosystems?.join(', ') || '-'}
                  </td>
                  <td>
                    <Link to={`/scans/${scan.scan_id}`} className="btn-link">Details</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
