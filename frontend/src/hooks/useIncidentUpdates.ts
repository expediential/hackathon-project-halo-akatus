"use client"

import { useEffect } from 'react'
import type { Incident } from '../types'

/**
 * Opt-in WebSocket bridge. It remains idle until NEXT_PUBLIC_INCIDENT_WS_URL
 * is configured by the backend team, avoiding any invented transport protocol.
 */
export function useIncidentUpdates(onIncident: (incident: Incident) => void) {
  useEffect(() => {
    const endpoint = process.env.NEXT_PUBLIC_INCIDENT_WS_URL
    if (!endpoint) return
    const socket = new WebSocket(endpoint)
    socket.onmessage = (message) => {
      try {
        const payload: unknown = JSON.parse(String(message.data))
        if (isIncidentUpdatedEvent(payload)) onIncident(payload.incident)
      } catch { /* Ignore malformed events; the current UI state remains reliable. */ }
    }
    return () => socket.close()
  }, [onIncident])
}

function isIncidentUpdatedEvent(value: unknown): value is { event: 'incident.updated'; incident: Incident } {
  return typeof value === 'object' && value !== null && 'event' in value && 'incident' in value && value.event === 'incident.updated'
}
