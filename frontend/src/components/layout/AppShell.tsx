"use client"

import type { ReactNode } from 'react'
import { Activity, Bell, BrainCircuit, ClipboardPlus, FlaskConical, LayoutDashboard, RadioTower, Siren, UsersRound } from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const links = [
  ['/', 'Dashboard', LayoutDashboard], ['/reports', 'Reports', RadioTower], ['/incidents', 'Incidents', Siren], ['/responder', 'Responder view', UsersRound], ['/intelligence', 'Intelligence', BrainCircuit], ['/alerts', 'Alerts', Bell], ['/reports/new', 'Submit Report', ClipboardPlus], ['/demo', 'Demo Scenario', FlaskConical],
] as const

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname()
  if (pathname === '/public') return <>{children}</>
  return <div className="app-shell"><aside className="sidebar"><div className="brand"><div className="brand-mark">ER</div><div><strong>EMERGENCY RESPONSE</strong><span>INTELLIGENCE CENTER</span></div></div><nav className="nav">{links.map(([to, label, Icon]) => { const active = to === '/' ? pathname === '/' : pathname === to || pathname.startsWith(`${to}/`); return <Link key={to} href={to} className={`nav-link ${active ? 'active' : ''}`}><Icon size={17} />{label}</Link> })}</nav><div className="side-footer"><b>INFORMATION SUPPORT</b>Evidence-led response workspace<br />Role: Operations Coordinator</div></aside><main className="main"><header className="topbar"><div className="topbar-title">Emergency Response Intelligence</div><div className="system-status"><span className="live-dot" /><Activity size={14} /> SYSTEM ONLINE</div></header>{children}</main></div>
}
