from datetime import datetime, timedelta, timezone
import unittest

from intelligence import IntelligenceEngine
from intelligence.actions import recommend_actions
from intelligence.confidence import assess_confidence, freshness
from intelligence.demo import demo_reports
from intelligence.normalization import normalize_report
from intelligence.priority import determine_priority, determine_severity


NOW = datetime(2026, 9, 23, 11, 0, tzinfo=timezone.utc)


def report(identifier, text, *, source="identified_eyewitness", timestamp="2026-09-23T10:45:00+00:00", **extra):
    return {"id": identifier, "description": text, "source_type": source, "timestamp": timestamp, **extra}


class FusionEngineTests(unittest.TestCase):
    def test_duplicate_reports_cluster(self):
        engine = IntelligenceEngine()
        engine.process_reports([
            report("R1", "Large fire at Block A."),
            report("R2", "Large fire at Block A."),
        ], now=NOW)
        incidents = engine.list_incidents()
        self.assertEqual(len(incidents), 1)
        self.assertEqual(incidents[0]["report_count"], 2)
        self.assertEqual(incidents[0]["explanation"]["matching"][0]["classification"], "duplicate")

    def test_unrelated_reports_remain_separate(self):
        engine = IntelligenceEngine()
        engine.process_reports([
            report("R1", "Fire at Block A."),
            report("R2", "Medical emergency at Block D."),
        ], now=NOW)
        self.assertEqual(len(engine.list_incidents()), 2)

    def test_related_descriptions_cluster_without_being_duplicate(self):
        engine = IntelligenceEngine()
        engine.process_reports([
            report("R1", "Large fire and smoke at Block A."),
            report("R2", "Flames visible around Block A."),
        ], now=NOW)
        result = engine.get_incident_for_report("R1")
        self.assertEqual(result["report_count"], 2)
        self.assertEqual(result["explanation"]["matching"][0]["classification"], "related")

    def test_contradictions_remain_visible(self):
        engine = IntelligenceEngine()
        engine.process_reports([
            report("R1", "Fire is active at Block A."),
            report("R2", "Fire has been extinguished at Block A.", source="authority"),
        ], now=NOW)
        result = engine.get_incident_for_report("R1")
        self.assertEqual(result["status"], "conflicting")
        self.assertEqual(result["contradictions"][0]["type"], "fire_status")
        self.assertEqual({fact["value"] for fact in result["uncertain_facts"]}, {"active", "extinguished"})

    def test_stale_information_loses_relevance_but_is_retained(self):
        old = NOW - timedelta(hours=2)
        self.assertEqual(freshness(old, NOW)[0], "outdated")
        engine = IntelligenceEngine()
        engine.process_report(report("OLD", "Fire at Block A.", timestamp=old.isoformat()), now=NOW)
        result = engine.get_incident_for_report("OLD")
        self.assertTrue(any(item["evidence_type"] == "OUTDATED_REPORT" for item in result["evidence"]))

    def test_corroboration_raises_confidence(self):
        single = [normalize_report(report("R1", "Fire at Block A."))]
        multiple = single + [normalize_report(report("R2", "Smoke at Block A.", source="security"))]
        self.assertGreater(assess_confidence(multiple, [], now=NOW)[0], assess_confidence(single, [], now=NOW)[0])

    def test_weak_source_is_not_verified(self):
        engine = IntelligenceEngine()
        result = engine.process_report(report("R1", "Fire is active at Block A.", source="social_media"), now=NOW)
        self.assertFalse(result["verified_facts"])
        self.assertLess(result["confidence"], .65)

    def test_severity_is_deterministic(self):
        observations = [normalize_report(report("R1", "Large active fire with trapped people at Block A."))]
        self.assertEqual(determine_severity(observations), "critical")
        self.assertEqual(determine_severity(observations), "critical")

    def test_priority_is_deterministic(self):
        observations = [normalize_report(report("R1", "Active fire at Block A."))]
        self.assertEqual(determine_priority("critical", observations, .8), "P0")
        self.assertEqual(determine_priority("critical", observations, .8), "P0")

    def test_actions_are_consistent_and_conservative(self):
        actions = recommend_actions("medical", [])
        self.assertEqual(actions, ["Request medical assistance.", "Keep the access route clear.", "Verify the affected-person count."])

    def test_unknown_information_is_preserved(self):
        observation = normalize_report({"id": "R1", "description": "Something happened.", "source_type": "social_media"})
        self.assertIsNone(observation.incident_type)
        self.assertIsNone(observation.location_name)
        self.assertIsNone(observation.people_affected)

    def test_raw_evidence_is_retained_without_mutating_input(self):
        original = report("R1", "Smoke at Blk-A.", metadata={"camera": "C7"})
        engine = IntelligenceEngine()
        engine.process_report(original, now=NOW)
        original["description"] = "Changed after submission"
        self.assertEqual(engine.get_raw_report("R1")["description"], "Smoke at Blk-A.")

    def test_missing_type_does_not_join_known_fire_just_by_location(self):
        engine = IntelligenceEngine()
        engine.process_reports([
            report("R1", "Fire at Block A."),
            report("R2", "Noise at Block A."),
        ], now=NOW)
        self.assertEqual(len(engine.list_incidents()), 2)

    def test_demo_uses_real_pipeline_to_produce_two_clusters(self):
        engine = IntelligenceEngine()
        engine.process_reports(demo_reports(), now=NOW)
        incidents = engine.list_incidents()
        self.assertEqual(len(incidents), 2)
        fire = next(item for item in incidents if item["type"] == "fire")
        self.assertEqual(fire["report_count"], 6)
        self.assertTrue(fire["contradictions"])


if __name__ == "__main__":
    unittest.main()
