import { ArrowUpRight, MapPin } from 'lucide-react'
import Link from 'next/link'
import type { Incident } from '../../types'
import { confidenceLabel, timeAgo } from '../../utils/format'
import { FreshnessBadge, SeverityBadge, StatusBadge } from '../common/ui'

export function IncidentCard({ incident }: { incident: Incident }) {
  return <article className={`incident-card ${incident.severity.toLowerCase()}`}><div className="incident-card-top"><div><SeverityBadge severity={incident.severity} /><h3>{incident.type}</h3><div className="incident-location"><MapPin size={12} />{incident.location.name}</div></div><Link className="linkish" href={`/incidents/${incident.incident_id}`} aria-label={`View ${incident.type} incident`}><ArrowUpRight size={17} /></Link></div><div className="card-meta"><span><b>{incident.priority}</b> priority</span><span><b>{incident.report_count}</b> reports</span><span><b>{incident.sourceCount}</b> sources</span><span>{timeAgo(incident.updated_at)}</span></div><div className="card-meta" style={{ marginTop: 10 }}><StatusBadge status={incident.informationStatus} /><span>Confidence <b>{confidenceLabel(incident.confidence)} · {incident.confidence}%</b></span><FreshnessBadge freshness={incident.freshness} /></div><div className="action-line"><b>RECOMMENDED ACTION</b>{incident.recommended_actions[0]?.title}</div></article>
}
