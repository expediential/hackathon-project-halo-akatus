import type { ReactNode } from 'react'
import { AlertTriangle, CheckCircle2, CircleDotDashed, Clock3 } from 'lucide-react'
import type { Freshness, InformationStatus, Severity } from '../../types'
import { freshnessClass, severityClass, statusClass } from '../../utils/format'

export function SeverityBadge({ severity }: { severity: Severity }) { return <span className={`tag ${severityClass[severity]}`}>{severity}</span> }
export function StatusBadge({ status }: { status: InformationStatus }) { return <span className={`state ${statusClass[status]}`}>{status === 'CONFLICTING' && <AlertTriangle size={11} />}{status === 'VERIFIED' && <CheckCircle2 size={11} />}{status === 'PROCESSING' && <CircleDotDashed size={11} />}{status}</span> }
export function FreshnessBadge({ freshness }: { freshness: Freshness }) { return <span className={`state ${freshnessClass[freshness]}`}>{freshness === 'OUTDATED' && <Clock3 size={11} />}{freshness}</span> }
export function Panel({ title, action, children, className = '' }: { title?: string; action?: ReactNode; children: ReactNode; className?: string }) { return <section className={`panel ${className}`}>{title && <header className="panel-header"><h2 className="panel-title">{title}</h2>{action}</header>}{children}</section> }
export function PageHeading({ eyebrow, title, description, action }: { eyebrow: string; title: string; description?: string; action?: ReactNode }) { return <div className="page-heading"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1>{description && <p>{description}</p>}</div>{action}</div> }
