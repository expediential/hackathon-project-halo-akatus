from intelligence.models import Contradiction

def recommend_actions(kind, contradictions):
    actions={'fire':['Evacuate the affected area.','Keep people away from the affected building.','Contact emergency services.','Verify evacuation routes.'], 'medical':['Request medical assistance.','Keep the access route clear.','Verify the affected-person count.'], 'flooding':['Keep people away from affected water areas.','Verify safe access routes.','Monitor for changes in water conditions.'], 'security':['Keep the affected area clear.','Verify current conditions with an appropriate responder.'], 'accident':['Keep the affected area clear.','Verify current conditions with an appropriate responder.']}.get(kind,['Obtain additional information and verify current conditions.'])
    return actions + (['Obtain an updated confirmation of the conflicting status.'] if contradictions else [])
