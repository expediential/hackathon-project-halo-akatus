# Intelligence / Data Fusion Engine

The intelligence package converts raw emergency reports into traceable incident clusters while retaining source reports, uncertainty, freshness, and conflicting claims. Its deterministic safety rules determine severity, P0–P3 priority, and conservative recommended actions.

Use `IntelligenceEngine().process_report(report)` as the stable backend boundary. Scores combine text, normalized location, time, incident type, source corroboration, evidence, and freshness. Confidence measures evidence strength, never verified truth.
