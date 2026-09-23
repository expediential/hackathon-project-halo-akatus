import { alerts, dashboardSummary, incidents, intelligenceMetrics, reports, timelineFor } from '../data/mockData'
import type { Alert, DashboardSummary, EmergencyReport, Incident, IntelligenceMetrics, ReportSubmission, TimelineEvent } from '../types'

const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? ''
const apiRequest = async <T>(path: string, fallback: T, init?: RequestInit): Promise<T> => {
  try {
    const response = await fetch(`${baseUrl}${path}`, { headers: { 'Content-Type': 'application/json' }, ...init })
    if (!response.ok) throw new Error(`API request failed: ${response.status}`)
    return await response.json() as T
  } catch { return fallback }
}

export const api = {
  getDashboardSummary: () => apiRequest<DashboardSummary>('/api/dashboard/summary', dashboardSummary),
  getDashboardIncidents: () => apiRequest<Incident[]>('/api/dashboard/incidents', incidents),
  getIncidents: () => apiRequest<Incident[]>('/api/incidents', incidents),
  getIncident: (id: string) => apiRequest<Incident | undefined>(`/api/incidents/${id}`, incidents.find((item) => item.incident_id === id)),
  getReports: () => apiRequest<EmergencyReport[]>('/api/reports', reports),
  getReport: (id: string) => apiRequest<EmergencyReport | undefined>(`/api/reports/${id}`, reports.find((item) => item.id === id)),
  submitReport: (payload: ReportSubmission) => apiRequest('/api/reports', { accepted: false, mode: 'mock' }, { method: 'POST', body: JSON.stringify(payload) }),
  getIncidentEvidence: (id: string) => apiRequest(`/api/intelligence/incidents/${id}/evidence`, incidents.find((item) => item.incident_id === id)?.evidence),
  getIncidentClaims: (id: string) => apiRequest(`/api/intelligence/incidents/${id}/claims`, incidents.find((item) => item.incident_id === id)?.claims ?? []),
  getIncidentConflicts: (id: string) => apiRequest(`/api/intelligence/incidents/${id}/conflicts`, incidents.find((item) => item.incident_id === id)?.contradictions ?? []),
  getIncidentTimeline: (id: string) => apiRequest<TimelineEvent[]>(`/api/intelligence/incidents/${id}/timeline`, timelineFor(id)),
  getIncidentExplanation: (id: string) => apiRequest(`/api/intelligence/incidents/${id}/explanation`, incidents.find((item) => item.incident_id === id)?.fusion),
  getIntelligenceMetrics: () => apiRequest<IntelligenceMetrics>('/api/intelligence/metrics', intelligenceMetrics),
  getAlerts: () => apiRequest<Alert[]>('/api/alerts', alerts),
  markAlertRead: (id: string) => apiRequest(`/api/alerts/${id}/read`, { id }, { method: 'PATCH' }),
  loadDemo: () => apiRequest('/api/demo/load', { accepted: false, mode: 'mock' }, { method: 'POST' }),
  resetDemo: () => apiRequest('/api/demo/reset', { accepted: false, mode: 'mock' }, { method: 'POST' }),
}
