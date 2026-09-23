export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
export type Priority = 'P0' | 'P1' | 'P2' | 'P3'
export type InformationStatus = 'VERIFIED' | 'CORROBORATED' | 'UNVERIFIED' | 'CONFLICTING' | 'OUTDATED' | 'PROCESSING'
export type Freshness = 'FRESH' | 'RECENT' | 'STALE' | 'OUTDATED'
export type IncidentStatus = 'ACTIVE' | 'CONTAINED' | 'RESOLVED' | 'UNKNOWN'
export type SourceType = 'Citizen' | 'Emergency Service' | 'Social Media' | 'CCTV/System' | 'Authority' | 'Other'

export interface Location { name: string; latitude?: number; longitude?: number; area?: string }
export interface RecommendedAction { title: string; reason: string; urgency: Severity }
export interface Conflict { id: string; summary: string; claims: string[]; requiresVerification: boolean }
export interface TimelineEvent { id: string; timestamp: string; title: string; detail?: string; status: InformationStatus }
export interface EmergencyReport {
  id: string; timestamp: string; source: SourceType; type: string; location: Location; status: InformationStatus; priority: Priority; incidentId?: string; text: string; extracted: { incidentType: string; location: string; indicators: string[] }
}
export interface IncidentEvidence { reportCount: number; sourceCount: number; reasons: string[]; caution?: string }
export interface IncidentClaim { text: string; supportingReports: number; status: InformationStatus }
export interface FusionExplanation { score: number; reasons: string[] }
export interface Incident {
  incident_id: string; type: string; severity: Severity; priority: Priority; confidence: number; status: IncidentStatus; informationStatus: InformationStatus; freshness: Freshness; location: Location; verified_facts: string[]; uncertain_facts: string[]; contradictions: Conflict[]; recommended_actions: RecommendedAction[]; report_count: number; sourceCount: number; created_at: string; updated_at: string; evidence: IncidentEvidence; claims: IncidentClaim[]; fusion?: FusionExplanation
}
export interface Alert { id: string; severity: Severity; title: string; message: string; timestamp: string; read: boolean; incidentId?: string }
export interface DashboardSummary { activeIncidents: number; critical: number; high: number; medium: number; low: number; unverified: number; conflicting: number; outdated: number }
export interface IntelligenceMetrics { reportsAnalyzed: number; potentialDuplicates: number; relatedReports: number; conflictsDetected: number; incidentsCreated: number; outdatedReports: number }
export interface ReportSubmission { source: SourceType; type: string; description: string; location: string; latitude?: number; longitude?: number; reportedAt: string }
