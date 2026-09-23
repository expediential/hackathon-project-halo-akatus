import type { Freshness, InformationStatus, Severity } from '../types'

export const severityClass: Record<Severity, string> = { CRITICAL: 'tag-critical', HIGH: 'tag-high', MEDIUM: 'tag-medium', LOW: 'tag-low' }
export const statusClass: Record<InformationStatus, string> = { VERIFIED: 'state-verified', CORROBORATED: 'state-corroborated', UNVERIFIED: 'state-unverified', CONFLICTING: 'state-conflicting', OUTDATED: 'state-outdated', PROCESSING: 'state-processing' }
export const freshnessClass: Record<Freshness, string> = { FRESH: 'state-verified', RECENT: 'state-corroborated', STALE: 'state-unverified', OUTDATED: 'state-outdated' }
export const dateTime = (value: string) => new Intl.DateTimeFormat('en-IN', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: 'short' }).format(new Date(value))
export const timeAgo = (value: string) => { const minutes = Math.max(1, Math.floor((Date.now() - new Date(value).getTime()) / 60000)); return minutes < 60 ? `${minutes} min ago` : `${Math.floor(minutes / 60)}h ago` }
export const confidenceLabel = (value: number) => value >= 80 ? 'HIGH' : value >= 55 ? 'MODERATE' : 'LOW'
