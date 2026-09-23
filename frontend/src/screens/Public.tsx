"use client"

import { AlertTriangle, ArrowRight, ShieldAlert } from 'lucide-react'
import { useEffect, useState } from 'react'
import type { Incident } from '../types'
import { api } from '../services/api'
import { dateTime } from '../utils/format'

export function Public() {
  const [incident, setIncident] = useState<Incident>()
  useEffect(() => { void api.getDashboardIncidents().then((items) => setIncident(items.find((item) => item.severity === 'CRITICAL') ?? items[0])) }, [])
  if (!incident) return <main className="public-view"><div className="loading">Loading verified public advisory…</div></main>
  return <main className="public-view"><header className="public-header"><ShieldAlert size={22} /> EMERGENCY RESPONSE ADVISORY</header><section className="public-card"><div className="eyebrow">ACTIVE EMERGENCY</div><h1>{incident.location.name}</h1><div className="public-type">{incident.type.toUpperCase()}</div><div className="public-action"><AlertTriangle size={24} /><div><b>EVACUATE USING EAST EXIT</b><span>Follow responder instructions at the assembly point.</span></div></div><div className="public-blocked">NORTH EXIT BLOCKED</div><p>Last verified: {dateTime(incident.updated_at)}</p><a className="btn" href="tel:112"><ArrowRight size={14} /> Call emergency services</a></section><footer>Only essential public safety information is shown here.</footer></main>
}
