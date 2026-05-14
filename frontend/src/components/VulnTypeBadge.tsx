import React from 'react'

interface Props { vulnType?: string; size?: 'sm' | 'md' }

const config: Record<string, { label: string; color: string; bg: string }> = {
  cve:                 { label: 'CVE',                  color: '#1d4ed8', bg: '#dbeafe' },
  supply_chain_attack: { label: 'Supply Chain Attack',  color: '#7c3aed', bg: '#ede9fe' },
  abandoned:           { label: 'Abandoned',            color: '#475569', bg: '#f1f5f9' },
  typosquatting:       { label: 'Typosquatting',        color: '#92400e', bg: '#fef3c7' },
}

export default function VulnTypeBadge({ vulnType = 'cve', size = 'md' }: Props) {
  const c = config[vulnType] || config.cve
  return (
    <span style={{
      display: 'inline-block',
      padding: size === 'sm' ? '2px 7px' : '3px 10px',
      borderRadius: 20,
      background: c.bg,
      color: c.color,
      fontSize: size === 'sm' ? '0.72rem' : '0.82rem',
      fontWeight: 600,
      whiteSpace: 'nowrap',
    }}>
      {c.label}
    </span>
  )
}
