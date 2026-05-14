import React from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import './Layout.css'

const navItems = [
  { to: '/', label: 'Dashboard', icon: '▦' },
  { to: '/scans', label: 'Scans', icon: '≡' },
  { to: '/vulnerabilities', label: 'Vulnerabilities', icon: '!' },
]

export default function Layout() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="sidebar-brand-icon">S</span>
          <span className="sidebar-brand-name">SCS Scanner</span>
        </div>
        <nav className="sidebar-nav">
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">v1.0.0</div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}
