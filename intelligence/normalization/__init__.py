import re
from datetime import datetime,timezone
from intelligence.models import ReportObservation
TYPES={'fire':('fire','flame','smoke','burning','blaze'),'medical':('medical','injury','injured','unconscious','ambulance'),'flooding':('flood','flooding','waterlogged'),'security':('security','intruder','suspicious','weapon'),'accident':('accident','collision','crash','vehicle'),'gas_leak':('gas leak','gas smell'),'collapse':('collapse','collapsed')}
def clean_text(v):return re.sub(r'\s+',' ',str(v or '').strip()).lower()
def normalize_location(v):
    text=clean_text(v)
    if not text:return None
    return re.sub(r'[-_/]',' ',re.sub(r'\bblk\.?\b','block',text)).title()
def parse_time(v,fallback=None):
    if isinstance(v,datetime):return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
    try:
        parsed=datetime.fromisoformat(str(v).replace('Z','+00:00'));return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except (ValueError,TypeError):return fallback
def infer_type(text):
    low=clean_text(text);return next((kind for kind,terms in TYPES.items() if any(x in low for x in terms)),None)
def extract_location(text):
    match=re.search(r'\b(?:near|at|in|around)\s+((?:block|blk|gate|building|road|floor)\s*[-#]?\s*[a-z0-9]+)',text,re.I);return normalize_location(match.group(1)) if match else None
def extract_claims(text,kind):
    low=clean_text(text); claims=[]
    if kind=='fire':claims += [{'type':'fire_status','value':'extinguished'}] if any(x in low for x in ('extinguished','put out')) else [{'type':'fire_status','value':'contained'}] if ('contained' in low or 'under control' in low) else [{'type':'fire_status','value':'active'}] if any(x in low for x in ('active','flames','burning','fire')) else []
    if any(x in low for x in ('exit blocked','route blocked','road blocked','traffic blocked')):claims.append({'type':'route_status','value':'blocked'})
    if any(x in low for x in ('exit clear','route clear','road clear','traffic clear')):claims.append({'type':'route_status','value':'clear'})
    return claims
def normalize_report(report):
    raw=dict(report); desc=str(raw.get('description') or raw.get('text') or '').strip(); received=parse_time(raw.get('received_at') or raw.get('created_at')) or datetime.now(timezone.utc); kind=clean_text(raw.get('incident_type')).replace(' ','_') if raw.get('incident_type') else infer_type(desc); location=normalize_location(raw.get('location') or raw.get('location_name')) or extract_location(desc); source=clean_text(raw.get('source_type') or 'anonymous_bystander').replace(' ','_'); people=raw.get('people_affected'); found=re.search(r'\b(\d+)\s+(?:people|persons|injured|casualties)\b',desc,re.I); people=people if people is not None else int(found.group(1)) if found else None; words=re.findall(r'[a-z0-9]+',clean_text(desc)); return ReportObservation(str(raw.get('id') or raw.get('report_id') or 'report'),str(raw.get('report_id') or raw.get('id') or 'report'),raw,desc,kind,location,raw.get('latitude'),raw.get('longitude'),parse_time(raw.get('timestamp') or raw.get('event_time'),received),received,source,people, list(raw.get('evidence') or []),[],{},extract_claims(desc,kind),words,desc,.7 if kind else .2)
