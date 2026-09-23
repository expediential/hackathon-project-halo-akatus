from datetime import datetime, timezone
DEFAULT_SOURCE_RELIABILITY={'authority':.95,'verified_responder':.90,'security':.85,'sensor':.85,'identified_eyewitness':.65,'anonymous_bystander':.50,'social_media':.35}
def freshness(event_time,now=None):
    if not event_time:return 'unknown',.45
    minutes=max(0,((now or datetime.now(timezone.utc))-event_time).total_seconds()/60)
    return ('fresh',1) if minutes<15 else ('recent',.85) if minutes<30 else ('stale',.60) if minutes<60 else ('outdated',.30)
def confidence_state(v): return 'very_low' if v<.2 else 'low' if v<.4 else 'medium' if v<.65 else 'high' if v<.85 else 'very_high'
def assess_confidence(reports,contradictions,now=None,source_reliability=None):
    if not reports:return 0.,'very_low',['no reports']
    priors=source_reliability or DEFAULT_SOURCE_RELIABILITY; source=sum(priors.get(r.source_type,.4) for r in reports)/len(reports); independent=len({r.source_type for r in reports}); corroboration=min(1,.25+.15*(len(reports)-1)+.1*(independent-1)); fresh=sum(freshness(r.event_time,now)[1] for r in reports)/len(reports); evidence=min(1,.35+.1*sum(bool(r.evidence) for r in reports)); value=max(0,min(1,.35*source+.30*corroboration+.20*fresh+.15*evidence-min(.35,.15*len(contradictions)))); return round(value,3),confidence_state(value),[f'{len(reports)} reports',f'{independent} independent source types',f'freshness contribution {fresh:.2f}']
