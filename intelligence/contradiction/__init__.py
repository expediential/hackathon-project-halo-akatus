from collections import defaultdict
from intelligence.confidence import freshness
from intelligence.models import IncidentClaim,Contradiction
def claims_from_reports(reports):
    result=[]
    for r in reports:
        state,weight=freshness(r.event_time)
        result += [IncidentClaim(c['type'],c['value'],r.report_id,weight,state,r.event_time or r.received_at) for c in r.claims]
    return result
def find_contradictions(claims):
    grouped=defaultdict(list)
    for c in claims:grouped[c.claim_type].append(c)
    return [Contradiction(kind,'contradicted',[{'value':c.claim_value,'report_id':c.source_report_id,'freshness':c.freshness} for c in group]) for kind,group in grouped.items() if len({c.claim_value for c in group})>1]
