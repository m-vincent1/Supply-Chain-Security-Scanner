import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend
} from 'recharts'
import { api } from '../api'
import type { ScanSummary } from '../types'
import SeverityBadge from '../components/SeverityBadge'
import './Dashboard.css'

const SEVERITY_COLORS = ['#c0392b', '#d35400', '#b7791f', '#276749']
const ECOSYSTEM_COLORS = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981']

export default function Dashboard() {
  const [scans, setScans] = useState<ScanSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.listScans(100)
      .then(setScans)
      .catch(() => setError('Unable to connect to the backend API.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="page-loading">Loading...</div>
  if (error) return <div className="page-error">{error}</div>

  const totalVulnerabilities = scans.reduce((sum, s) => sum + s.total_vulnerabilities, 0)
  const criticalCount = scans.reduce((sum, s) => sum + (s.vulnerabilities_by_severity?.critical || 0), 0)
  const highCount = scans.reduce((sum, s) => sum + (s.vulnerabilities_by_severity?.high || 0), 0)
  const avgScore = scans.length > 0
    ? Math.round(scans.reduce((sum, s) => sum + s.risk_score, 0) / scans.length)
    : 0

  const severityData = [
    { name: 'Critical', value: criticalCount },
    { name: 'High', value: highCount },
    { name: 'Medium', value: scans.reduce((sum, s) => sum + (s.vulnerabilities_by_severity?.medium || 0), 0) },
    { name: 'Low', value: scans.reduce((sum, s) => sum + (s.vulnerabilities_by_severity?.low || 0), 0) },
  ]

  const ecosystemMap: Record<string, number> = {}
  scans.forEach(s => s.ecosystems?.forEach(e => { ecosystemMap[e] = (ecosystemMap[e] || 0) + 1 }))
  const ecosystemData = Object.entries(ecosystemMap).map(([name, value]) => ({ name, value }))

  const topRiskyScans = [...scans].sort((a, b) => b.risk_score - a.risk_score).slice(0, 5)

  return (
    <div className="page">
      <h1 className="page-title">Dashboard</h1>

      <div className="stat-grid">
        {[
          { label: 'Total scans', value: scans.length, color: '#3b82f6' },
          { label: 'Average risk score', value: `${avgScore}/100`, color: avgScore > 50 ? '#c0392b' : '#276749' },
          { label: 'Critical findings', value: criticalCount, color: '#c0392b' },
          { label: 'High findings', value: highCount, color: '#d35400' },
          { label: 'Total vulnerabilities', value: totalVulnerabilities, color: '#b7791f' },
        ].map(s => (
          <div className="stat-card" key={s.label}>
            <div className="stat-label">{s.label}</div>
            <div className="stat-value" style={{ color: s.color }}>{s.value}</div>
          </div>
        ))}
      </div>

      <div className="charts-grid">
        <div className="card">
          <h2 className="card-title">Vulnerabilities by severity</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={severityData} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {severityData.map((_, i) => <Cell key={i} fill={SEVERITY_COLORS[i]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2 className="card-title">Scans by ecosystem</h2>
          {ecosystemData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={ecosystemData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                  {ecosystemData.map((_, i) => <Cell key={i} fill={ECOSYSTEM_COLORS[i % ECOSYSTEM_COLORS.length]} />)}
                </Pie>
                <Legend />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state">No scan data available yet.</div>
          )}
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">Top projects at risk</h2>
        {topRiskyScans.length === 0 ? (
          <div className="empty-state">
            No scans yet. Run <code>scs-scanner scan &lt;path&gt;</code> or use the API to create a scan.
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Project</th>
                <th>Risk Score</th>
                <th>Level</th>
                <th>Vulnerabilities</th>
                <th>Dependencies</th>
                <th>Date</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {topRiskyScans.map(scan => (
                <tr key={scan.scan_id}>
                  <td><strong>{scan.project_name}</strong></td>
                  <td>{scan.risk_score}/100</td>
                  <td><SeverityBadge severity={scan.risk_level.toLowerCase() as any} size="sm" /></td>
                  <td>{scan.total_vulnerabilities}</td>
                  <td>{scan.total_dependencies}</td>
                  <td>{new Date(scan.scan_date).toLocaleDateString()}</td>
                  <td><Link to={`/scans/${scan.scan_id}`} className="btn-link">View</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
