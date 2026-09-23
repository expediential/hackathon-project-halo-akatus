def determine_severity(reports):
    text=' '.join(r.description.lower() for r in reports)
    if any(x in text for x in ('trapped','mass casualty','structural collapse','immediate life threat')) or any(r.incident_type=='fire' and any(x in r.description.lower() for x in ('active','flames','large','huge')) for r in reports):return 'critical'
    if any(x in text for x in ('serious injur','gas leak','blocked evacuation','rapidly escalating')):return 'high'
    return 'medium' if any(r.incident_type in {'flooding','security','medical','accident'} for r in reports) else 'low'
def determine_priority(severity,reports,confidence,geographic_relevance=1.):
    score={'critical':4,'high':3,'medium':2,'low':1}[severity]+int(any('active' in r.description.lower() or 'now' in r.description.lower() for r in reports))+int(confidence>=.65)+int(geographic_relevance>=.75)+ (2 if max((r.people_affected or 0 for r in reports),default=0)>=10 else 1 if any(r.people_affected for r in reports) else 0)
    return 'P0' if score>=7 else 'P1' if score>=5 else 'P2' if score>=3 else 'P3'
