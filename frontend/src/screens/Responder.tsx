"use client"

import { Radio, ShieldCheck, Truck } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from '../components/common/Link'
import { FreshnessBadge, PageHeading, Panel, SeverityBadge, StatusBadge } from '../components/common/ui'
import { api } from '../services/api'
import type { Incident } from '../types'
import { dateTime } from '../utils/format'

export function Responder() {
  const [incidents, setIncidents] = useState<Incident[]>([])
  useEffect(() => { void api.getIncidents().then((items) => setIncidents(items.filter((item) => item.status === 'ACTIVE').sort((a, b) => a.priority.localeCompare(b.priority)))) }, [])
  return <main className="page"><PageHeading eyebrow="Restricted operational view" title="Responder coordination" description="Operational detail for assigned response teams. Verify changing conditions through command channels before acting." /><div className="section-stack">{incidents.map((incident) => <Panel key={incident.incident_id} title={`${incident.priority} · ${incident.type}`} action={<div style={{ display: 'flex', gap: 7 }}><SeverityBadge severity={incident.severity} /><FreshnessBadge freshness={incident.freshness} /></div>}><div className="panel-body detail-grid"><div><div className="overview"><div className="overview-item"><span>Location</span><b>{incident.location.name}</b></div><div className="overview-item"><span>Response status</span><StatusBadge status={incident.informationStatus} /></div><div className="overview-item"><span>Evidence</span><b>{incident.report_count} reports / {incident.sourceCount} source types</b></div><div className="overview-item"><span>Last update</span><b>{dateTime(incident.updated_at)}</b></div></div><div className="notice" style={{ marginTop: 14 }}><Truck size={15} style={{ verticalAlign: 'middle', marginRight: 7 }} /><b>Recommended action:</b> {incident.recommended_actions[0]?.title}<br /><span className="muted">{incident.recommended_actions[0]?.reason}</span></div></div><div className="section-stack"><div className="conflict-box"><Radio size={14} style={{ verticalAlign: 'middle', marginRight: 6 }} /><b>Operational check</b><br />{incident.contradictions.length ? incident.contradictions[0].summary : 'No conflicts currently detected.'}</div><Link className="btn" to={`/incidents/${incident.incident_id}`}><ShieldCheck size={14} /> Review full evidence</Link></div></div></Panel>)}{!incidents.length && <div className="loading">Loading responder assignments…</div>}</div></main>
}
