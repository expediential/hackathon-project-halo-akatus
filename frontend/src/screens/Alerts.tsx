"use client"

import { BellRing, Check, CircleAlert } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from '../components/common/Link'
import { PageHeading, SeverityBadge } from '../components/common/ui'
import { api } from '../services/api'
import type { Alert } from '../types'
import { dateTime } from '../utils/format'

export function Alerts() { const [items, setItems] = useState<Alert[]>([]); useEffect(() => { void api.getAlerts().then(setItems) }, []); const markRead = async (id: string) => { await api.markAlertRead(id); setItems((current) => current.map((item) => item.id === id ? { ...item, read: true } : item)) }; return <main className="page"><PageHeading eyebrow="Operational signals" title="Alerts" description="Backend-generated signals requiring visibility or follow-up. Marking an alert read acknowledges it; it does not resolve the incident." /><div className="alert-list">{items.map((alert) => <article className={`alert-item ${alert.read ? '' : 'unread'}`} key={alert.id}><div className="alert-icon"><CircleAlert color={alert.severity === 'CRITICAL' ? '#ec6464' : '#e7ae55'} size={20} /></div><div className="alert-copy"><div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}><SeverityBadge severity={alert.severity} /><h3>{alert.title}</h3></div><p>{alert.message}</p><span className="muted">{dateTime(alert.timestamp)}</span>{alert.incidentId && <Link className="linkish" style={{ marginLeft: 12 }} to={`/incidents/${alert.incidentId}`}>View incident</Link>}</div>{!alert.read && <button className="btn" onClick={() => void markRead(alert.id)}><Check size={14} /> Mark read</button>}</article>)}{!items.length && <div className="empty panel"><BellRing size={20} /> No alerts are available.</div>}</div></main> }
