import React from 'react'
import type { RiskLevel } from '../types'

interface Props { score: number; level: RiskLevel; size?: number }

const levelColors: Record<RiskLevel, string> = {
  Critical: '#c0392b',
  High: '#d35400',
  Medium: '#b7791f',
  Low: '#276749',
}

export default function ScoreGauge({ score, level, size = 80 }: Props) {
  const color = levelColors[level] || '#276749'
  return (
    <div style={{
      display: 'inline-flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: 4,
    }}>
      <div style={{
        width: size,
        height: size,
        borderRadius: '50%',
        border: `6px solid ${color}`,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: color + '18',
      }}>
        <span style={{ fontWeight: 700, fontSize: size * 0.26, color, lineHeight: 1 }}>{score}</span>
        <span style={{ fontSize: size * 0.13, color: '#666' }}>/100</span>
      </div>
      <span style={{ fontSize: '0.8rem', fontWeight: 600, color }}>{level}</span>
    </div>
  )
}
