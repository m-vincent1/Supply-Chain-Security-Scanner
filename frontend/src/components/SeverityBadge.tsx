import React from 'react'
import type { Severity } from '../types'

interface Props { severity: Severity; size?: 'sm' | 'md' }

const colors: Record<Severity, { bg: string; text: string }> = {
  critical: { bg: '#fde8e8', text: '#c0392b' },
  high:     { bg: '#fef3e0', text: '#d35400' },
  medium:   { bg: '#fff8e1', text: '#b7791f' },
  low:      { bg: '#e6f4ea', text: '#276749' },
}

export default function SeverityBadge({ severity, size = 'md' }: Props) {
  const c = colors[severity] || colors.low
  return (
    <span style={{
      display: 'inline-block',
      padding: size === 'sm' ? '2px 8px' : '3px 10px',
      borderRadius: 20,
      background: c.bg,
      color: c.text,
      fontSize: size === 'sm' ? '0.75rem' : '0.82rem',
      fontWeight: 600,
      textTransform: 'uppercase',
      letterSpacing: '0.03em',
    }}>
      {severity}
    </span>
  )
}
