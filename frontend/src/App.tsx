import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ScanList from './pages/ScanList'
import ScanDetail from './pages/ScanDetail'
import Vulnerabilities from './pages/Vulnerabilities'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/scans" element={<ScanList />} />
          <Route path="/scans/:id" element={<ScanDetail />} />
          <Route path="/vulnerabilities" element={<Vulnerabilities />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
