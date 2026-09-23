import unittest
from datetime import datetime,timezone
from intelligence import IntelligenceEngine
NOW=datetime(2026,9,23,11,tzinfo=timezone.utc)
def r(i,text,source='identified_eyewitness'): return {'id':i,'description':text,'timestamp':'2026-09-23T10:45:00+00:00','source_type':source}
class TestFusion(unittest.TestCase):
 def test_cluster(self):
  e=IntelligenceEngine();e.process_reports([r('1','Large fire at Block A.'),r('2','Flames visible at Block A.')],now=NOW);self.assertEqual(len(e.list_incidents()),1)
 def test_conflict(self):
  e=IntelligenceEngine();e.process_reports([r('1','Fire is active at Block A.'),r('2','Fire has been extinguished at Block A.','authority')],now=NOW);self.assertEqual(e.get_incident_for_report('1')['status'],'conflicting')
 def test_unrelated(self):
  e=IntelligenceEngine();e.process_reports([r('1','Fire at Block A.'),r('2','Medical emergency at Block D.')],now=NOW);self.assertEqual(len(e.list_incidents()),2)
if __name__=='__main__':unittest.main()
