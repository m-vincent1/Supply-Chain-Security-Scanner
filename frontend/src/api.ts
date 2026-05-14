import axios from 'axios'
import type { ScanSummary, ScanResult, VulnerabilityEntry } from './types'

const client = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

export const api = {
  listScans: (limit = 50, offset = 0): Promise<ScanSummary[]> =>
    client.get('/scans', { params: { limit, offset } }).then(r => r.data),

  getScan: (id: string): Promise<ScanResult> =>
    client.get(`/scans/${id}`).then(r => r.data),

  getScanSBOM: (id: string) =>
    client.get(`/scans/${id}/sbom`).then(r => r.data),

  getScanReport: (id: string, format: string): Promise<{ content: string }> =>
    client.get(`/scans/${id}/report`, { params: { format } }).then(r => r.data),

  createScan: (projectPath: string, projectName?: string): Promise<ScanSummary> =>
    client.post('/scans', { project_path: projectPath, project_name: projectName }).then(r => r.data),

  listVulnerabilities: (ecosystem?: string, severity?: string): Promise<VulnerabilityEntry[]> =>
    client.get('/vulnerabilities', { params: { ecosystem, severity } }).then(r => r.data),

  health: () =>
    axios.get('/health').then(r => r.data),
}
