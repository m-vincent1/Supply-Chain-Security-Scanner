export type Severity = 'critical' | 'high' | 'medium' | 'low'
export type RiskLevel = 'Critical' | 'High' | 'Medium' | 'Low'
export type Ecosystem = 'python' | 'npm' | 'maven'
export type ScanStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface RiskScore {
  total: number
  level: RiskLevel
  breakdown: Record<string, number>
}

export interface ScanSummary {
  scan_id: string
  project_name: string
  scan_date: string
  risk_score: number
  risk_level: RiskLevel
  status: ScanStatus
  total_dependencies: number
  total_vulnerabilities: number
  vulnerabilities_by_severity: Record<string, number>
  ecosystems: string[]
}

export interface DetectedVulnerability {
  vulnerability_id: string
  package: string
  installed_version: string | null
  ecosystem: Ecosystem
  severity: Severity
  cvss: number
  summary: string
  recommendation: string
  affected_versions: string
  references: string[]
}

export interface Remediation {
  package: string
  ecosystem: Ecosystem
  risk: string
  impact: string
  evidence: string
  action: string
  suggested_command: string | null
  priority: Severity
}

export interface SBOMComponent {
  name: string
  version: string | null
  ecosystem: Ecosystem
  source_file: string
  dependency_type: string
}

export interface SBOM {
  project_name: string
  scan_date: string
  scanner_version: string
  ecosystems: string[]
  components: SBOMComponent[]
}

export interface Component {
  name: string
  version: string | null
  ecosystem: Ecosystem
  source_file: string
  dependency_type: string
  is_pinned: boolean
}

export interface ScanResult {
  scan_id: string
  project_name: string
  scanned_path: string
  scan_date: string
  scanner_version: string
  total_dependencies: number
  total_vulnerabilities: number
  vulnerabilities_by_severity: Record<string, number>
  risk_score: RiskScore
  components: Component[]
  vulnerabilities: DetectedVulnerability[]
  remediations: Remediation[]
  sbom: SBOM
  ecosystems: string[]
  analysis_limits: string[]
}

export interface VulnerabilityEntry {
  id: string
  package: string
  ecosystem: Ecosystem
  affected_versions: string
  severity: Severity
  cvss: number
  summary: string
  recommendation: string
  references: string[]
}
