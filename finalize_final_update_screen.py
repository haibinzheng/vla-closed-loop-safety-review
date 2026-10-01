from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PACKAGE_MODE = (HERE / "final_search_records.csv").exists()
ROOT = HERE.parents[0] if not PACKAGE_MODE else HERE
SUPP = HERE if PACKAGE_MODE else ROOT / "01_PAPER" / "TEX4" / "supplement"
SCREEN = SUPP / "final_update_screen.csv"
SYNTHESIS = SUPP / "final_update_qualitative_synthesis.csv"
SUMMARY = SUPP / "final_update_screen_summary.json"

EXCLUDE_FULL_TEXT = {
    "2607.27782": "Ordinary task-failure correction through offline policy learning; no declared safety property or safety endpoint.",
    "2608.13395": "Failure-informed driving-policy training evaluates reward and task performance rather than a closed-loop safety property.",
    "2609.03142": "Training-time modality robustness evaluates task performance without a declared safety endpoint.",
    "2609.06114": "Failure-boundary learning improves adaptation and task success but does not evaluate a declared runtime safety property.",
}

SYNTHESIS_MAP = {
    "2607.26789": ("RQ2;RQ3;RQ4", "Core", "signal-verdict-authority-response-execution-transition", "Adds action-conditioned execution verification, calibrated intervention, and latency-aware repair in simulation."),
    "2607.27881": ("RQ2;RQ3;RQ4", "Core", "signal-verdict-authority-response-execution-transition", "Adds monitored hierarchical recovery and replanning across simulation and real-robot case studies."),
    "2607.27933": ("RQ2", "Core", "signal-verdict", "Adds a flow-field uncertainty signal; does not by itself establish authorized intervention or outcome verification."),
    "2607.29169": ("RQ2;RQ3;RQ4", "Core", "signal-verdict-response-execution-transition", "Adds a same-system runtime safeguard with disturbance-specific mitigation and resumption evidence."),
    "2607.29569": ("RQ3;RQ5", "Core", "authority-response-execution", "Adds barrier-constrained action-chunk generation with formal assumptions and bounded validation."),
    "2608.00315": ("RQ3;RQ5", "Bridge", "verdict-authority-response-execution", "Adds language-conditioned runtime safety filtering; transfer remains constraint-family bounded."),
    "2608.03207": ("RQ1", "Core", "origin-propagation-outcome", "Adds a denoising-trajectory attack surface and a limited compression defense baseline."),
    "2608.03231": ("RQ1;RQ3", "Core", "origin-propagation-response-outcome", "Adds a physical attention-hijacking attack and training-time defense."),
    "2608.04246": ("RQ2;RQ5", "Core", "signal-verdict", "Adds shift-aware calibrated failure detection; no executed mitigation is demonstrated."),
    "2608.04510": ("RQ2", "Core", "signal-verdict", "Adds counterfactual grounding diagnostics across policies and domains; intervention remains downstream."),
    "2608.04692": ("RQ3;RQ5", "Core", "response-execution-outcome", "Shows that closed-loop behavior removal can suppress targets while degrading control skills; no general locality guarantee."),
    "2608.10393": ("RQ1", "Core", "origin-propagation-outcome", "Adds natural-looking physical attack evidence under white- and black-box access."),
    "2608.13453": ("RQ1", "Core", "origin-propagation-outcome", "Adds cross-task universal physical-texture attacks."),
    "2608.13474": ("RQ2", "Core", "signal-verdict", "Adds a readable progress signal and label-free OOD detector; no control authority is attached."),
    "2608.14822": ("RQ3;RQ4", "Core", "verdict-response-execution-transition", "Adds training-free counterfactual realignment and return-to-policy logic."),
    "2608.15475": ("RQ1", "Core", "origin-propagation-outcome", "Adds a deployed weight-fault surface with architecture-dependent vulnerability."),
    "2608.16697": ("RQ2;RQ3", "Core", "signal-verdict-response", "Adds model-intrinsic reliability scoring and verifier-free candidate selection; executed recovery is not shown."),
    "2608.17095": ("RQ3;RQ5", "Bridge", "authority-response", "Adds bounded inference-time attention steering and explicitly shows that text-path invariance is exposure, not robustness."),
    "2608.17496": ("RQ2;RQ3;RQ5", "Bridge", "signal-verdict-authority-response-execution", "Adds calibrated candidate-risk prediction coupled to a hard model-based shield and fallback ladder."),
    "2608.17600": ("RQ1;RQ5", "Core", "origin-outcome", "Adds an authorized-versus-unauthorized visual-cue benchmark; it does not demonstrate runtime recovery."),
    "2608.17717": ("RQ3;RQ5", "Bridge", "property-authority-execution-outcome", "Adds sound multimodal intent sets and closed-loop execution, including physical trials."),
    "2608.20556": ("RQ3;RQ5", "Core", "property-response-execution-outcome", "Adds inference-time temporal-logic conditioning evaluated in closed-loop simulation."),
    "2608.20791": ("RQ2;RQ3;RQ5", "Core", "signal-verdict-response-execution-outcome", "Adds calibrated closed-loop action certificates under bounded patch and texture attacks."),
    "2608.25757": ("RQ2", "Core", "signal-verdict", "Adds jointly trained progress, event, and action-uncertainty signals with advance warning evidence."),
    "2608.26578": ("RQ1", "Core", "origin-propagation-outcome", "Adds configurable backdoor failure modes rather than undifferentiated task failure."),
    "2608.26645": ("RQ3;RQ4", "Core", "signal-verdict-authority-response-execution-transition", "Adds online failure arbitration between retry and reset skills and task resumption."),
    "2608.29583": ("RQ2", "Core", "signal-verdict", "Adds reasoning-trajectory consistency monitoring in a driving VLA; no executed safety response is evaluated."),
    "2608.29967": ("RQ3;RQ4", "Core", "authority-response-execution-transition", "Adds one-shot task-level language correction in simulation and physical experiments."),
    "2609.04277": ("RQ2", "Core", "signal-verdict", "Adds timestamp-level failure detection and localization."),
    "2609.05178": ("RQ4;RQ5", "Core", "failure-transition-outcome", "Adds a four-level recovery benchmark spanning retry, adaptation, object recovery, and environmental recovery."),
    "2609.05832": ("RQ2;RQ3", "Core", "signal-response-execution-timing", "Adds force-aware reactive control and exposes action-chunk latency as a safety-relevant constraint."),
    "2609.06508": ("RQ2;RQ3;RQ4", "Core", "signal-verdict-authority-response-execution-transition", "Adds stage-aware observable-state verification and prompt-based closed-loop recovery."),
    "2609.09250": ("RQ5", "Adjacent", "verdict-validation", "Adds an overlapping verifier survey organized by availability and credibility; useful for positioning rather than primary effect evidence."),
    "2609.11697": ("RQ3;RQ5", "Core", "property-response-execution", "Adds differentiable per-step constraint enforcement with real-robot validation; claims remain conditional on the specified feasible region."),
    "2609.12371": ("RQ1;RQ3", "Bridge", "risk-representation-response-outcome", "Adds an explicit risk field for trajectory evaluation and refinement in driving, including a VLA setting."),
    "2609.13231": ("RQ3;RQ5", "Core", "property-authority-response-execution", "Adds reachability-informed safety alignment; guarantees inherit the learned critic and evaluated operating assumptions."),
    "2609.15005": ("RQ1;RQ5", "Core", "origin-propagation-outcome", "Adds closed-loop counterfactual propagation attribution and separates functional from behavioral recovery."),
    "2609.15940": ("RQ5", "Core", "evaluation-outcome", "Adds paired compound-robustness evaluation showing that single-axis results do not compose mechanically."),
    "2609.11445": ("RQ2;RQ5", "Core", "signal-verdict-timing", "Adds low-latency causal failure readout from frozen predictive states across simulated and physical platforms."),
    "2609.13236": ("RQ5", "Adjacent", "property-authority-validation", "Adds a governance-oriented framework for constraining post-deployment self-evolution; it does not supply primary closed-loop effect evidence."),
    "10.3390/e28090975": ("RQ1;RQ3", "Core", "signal-response-execution-outcome", "Adds stream-specific OOD gates and restoration with paired and prospective evaluation."),
}


with SCREEN.open("r", encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle))

synthesis = []
for row in rows:
    arxiv = row.get("arxiv_id", "")
    doi = row.get("doi", "").lower()
    key = arxiv if arxiv in SYNTHESIS_MAP or arxiv in EXCLUDE_FULL_TEXT else doi
    if row["initial_screen_decision"] == "Retrieve_Full_Text":
        if PACKAGE_MODE and row.get("full_text_status") in {"PDF_Checked", "Publisher_Full_Text_Checked", "Authoritative_HTML_Checked"}:
            pass
        elif arxiv and (ROOT / row["full_text_path"]).exists():
            row["full_text_status"] = "PDF_Checked"
        elif doi == "10.3390/e28090975":
            row["full_text_status"] = "Publisher_Full_Text_Checked"
        elif arxiv in {"2607.26789", "2607.27881", "2609.11445", "2609.13236"}:
            row["full_text_status"] = "Authoritative_HTML_Checked"
        else:
            row["full_text_status"] = "Source_Deferred"

        if arxiv in EXCLUDE_FULL_TEXT:
            row["eligibility_decision"] = "Exclude_After_Full_Text"
            row["eligibility_reason"] = EXCLUDE_FULL_TEXT[arxiv]
        elif key in SYNTHESIS_MAP and row["full_text_status"] != "Source_Deferred":
            row["eligibility_decision"] = "Include_Late_Update_Sensitivity"
            row["eligibility_reason"] = "Meets at least one RQ-linked eligibility criterion; retained outside the frozen 254-claim descriptive counts."
            rq, relation, links, implication = SYNTHESIS_MAP[key]
            synthesis.append({
                "screen_id": row["screen_id"],
                "title": row["title"],
                "year": "2026",
                "doi": doi,
                "arxiv_id": arxiv,
                "rq_contribution": rq,
                "evidence_relation": relation,
                "observed_links": links,
                "effect_on_review": implication,
                "counting_rule": "Qualitative late-update sensitivity only; excluded from the frozen 56-study, 254-claim, and 2,140-cell counts.",
            })
        else:
            row["eligibility_decision"] = "Source_Deferred"
            row["eligibility_reason"] = "Authoritative full text was not obtained; no eligibility or effect claim is made."

with SCREEN.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

with SYNTHESIS.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(synthesis[0].keys()))
    writer.writeheader()
    writer.writerows(synthesis)

summary = {
    "screened_priority_records": len(rows),
    "initial_decisions": dict(Counter(x["initial_screen_decision"] for x in rows)),
    "full_text_status": dict(Counter(x["full_text_status"] for x in rows)),
    "final_eligibility": dict(Counter(x["eligibility_decision"] for x in rows)),
    "late_update_sensitivity_studies": len(synthesis),
}
SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(summary, indent=2, ensure_ascii=False))
