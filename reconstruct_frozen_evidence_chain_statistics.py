#!/usr/bin/env python3
"""Reconstruct the frozen evidence-chain statistics from released source tables."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CLAIMS = ROOT / "status_closed_claims.csv"
LINKS = ROOT / "claim_experiment_links.csv"
AUDITED = ROOT / "evidence_chain_statistics.csv"
DEFAULT_OUTPUT = ROOT / "reconstructed_evidence_chain_statistics.csv"

MISSING = {"", "None", "None_Identified", "NR", "NA", "N/A", "Not_Applicable"}
OPERATIONAL_SETTINGS = {
    "Closed_Loop_Simulation",
    "Controlled_Real_Robot",
    "Mixed_Settings",
    "Field_Deployment",
}
EXECUTION_FUNCTIONS = {"Intervention_Evidence", "Evaluation_Evidence", "Recovery_Evidence"}
OUTCOME_FUNCTIONS = {"Evaluation_Evidence", "Performance_Evidence"}
RELATION_ORDER = {"Core": 0, "Bridge": 1, "Adjacent": 2}


def present(value: str) -> bool:
    return value.strip() not in MISSING


def executed(claim: dict[str, str]) -> bool:
    return (
        claim["Claim_Function"] in EXECUTION_FUNCTIONS
        and claim["Evidence_Setting"] in OPERATIONAL_SETTINGS
        and present(claim["Intervention_Mechanism"])
    )


def outcome(claim: dict[str, str]) -> bool:
    return (
        claim["Claim_Function"] in OUTCOME_FUNCTIONS
        and claim["Evidence_Setting"] in OPERATIONAL_SETTINGS
    )


def pct(count: int, denominator: int) -> str:
    return f"{100 * count / denominator:.1f}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Compare reconstructed rows with evidence_chain_statistics.csv.",
    )
    args = parser.parse_args()

    with CLAIMS.open("r", encoding="utf-8-sig", newline="") as handle:
        claims = list(csv.DictReader(handle))
    with LINKS.open("r", encoding="utf-8-sig", newline="") as handle:
        link_rows = list(csv.DictReader(handle))

    claim_by_id = {claim["Claim_ID"]: claim for claim in claims}
    experiments_by_claim: dict[str, set[str]] = defaultdict(set)
    for row in link_rows:
        experiment_id = row["Experiment_ID"].strip()
        if experiment_id:
            experiments_by_claim[row["Claim_ID"]].add(experiment_id)

    studies = {claim["Study_Title"] for claim in claims}
    linked_experiments = {exp for values in experiments_by_claim.values() for exp in values}
    if len(claims) != 254 or len(studies) != 56 or len(linked_experiments) != 891:
        raise ValueError(
            "Frozen denominator mismatch: expected 254 claims, 56 studies, and 891 claim-linked experiment cells; "
            f"found {len(claims)}, {len(studies)}, and {len(linked_experiments)}."
        )

    stages = [
        ("Risk signal", lambda c: present(c["Observable_Signal"]), "Non-missing Observable_Signal"),
        ("Monitor verdict", lambda c: present(c["Monitor_Method"]), "Non-missing Monitor_Method"),
        ("Authority", lambda c: present(c["Intervention_Authority"]), "Non-missing Intervention_Authority"),
        ("Selected response", lambda c: present(c["Intervention_Mechanism"]), "Non-missing Intervention_Mechanism"),
        (
            "Executed response",
            executed,
            "Operational non-offline/non-conceptual intervention/evaluation/recovery claim with a response",
        ),
        (
            "Observed outcome",
            outcome,
            "Operational non-offline/non-conceptual evaluation/performance claim",
        ),
    ]

    rows: list[dict[str, str | int]] = []

    def add(panel: str, measure: str, category: str, unit: str, count: int, denominator: int, definition: str) -> None:
        rows.append(
            {
                "Panel": panel,
                "Measure": measure,
                "Category": category,
                "Unit": unit,
                "Count": count,
                "Denominator": denominator,
                "Percent": pct(count, denominator),
                "Definition": definition,
            }
        )

    study_definitions = {
        "Risk signal": "At least one claim has a non-missing Observable_Signal",
        "Monitor verdict": "At least one claim has a non-missing Monitor_Method",
        "Authority": "At least one claim has a non-missing Intervention_Authority",
        "Selected response": "At least one claim has a non-missing Intervention_Mechanism",
    }
    for measure, predicate, definition in stages:
        matched = [claim for claim in claims if predicate(claim)]
        add(
            "Stage coverage",
            measure,
            "All included evidence",
            "Study",
            len({claim["Study_Title"] for claim in matched}),
            len(studies),
            study_definitions.get(measure, definition),
        )
    for measure, predicate, definition in stages:
        matched = [claim for claim in claims if predicate(claim)]
        add("Stage coverage", measure, "All included evidence", "Claim", len(matched), len(claims), definition)
    for measure, predicate, definition in stages:
        matched_ids = {claim["Claim_ID"] for claim in claims if predicate(claim)}
        experiments = {
            experiment
            for claim_id in matched_ids
            for experiment in experiments_by_claim.get(claim_id, set())
        }
        exp_definition = (
            "Experiment cell inherits the operational execution stage from at least one linked claim"
            if measure == "Executed response"
            else "Experiment cell inherits an operational outcome stage from at least one linked claim"
            if measure == "Observed outcome"
            else "Experiment cell inherits the stage from at least one linked claim"
        )
        add("Stage coverage", measure, "Linked evidence", "Experiment cell", len(experiments), len(linked_experiments), exp_definition)

    interfaces = [
        (
            "Verdict to authority",
            lambda c: present(c["Monitor_Method"]) and present(c["Intervention_Authority"]),
            "Same atomic claim has both fields and at least one non-empty experiment link; study assigned highest relation Core over Bridge over Adjacent",
        ),
        (
            "Response to execution",
            lambda c: present(c["Intervention_Mechanism"]) and executed(c),
            "Same atomic claim has selected response and operational execution evidence with at least one non-empty experiment link",
        ),
        (
            "Execution to outcome",
            lambda c: executed(c) and outcome(c),
            "Same atomic claim has operational execution and outcome evidence with at least one non-empty experiment link",
        ),
    ]
    for measure, predicate, definition in interfaces:
        qualifying = [
            claim
            for claim in claims
            if predicate(claim) and experiments_by_claim.get(claim["Claim_ID"])
        ]
        relations_by_study: dict[str, set[str]] = defaultdict(set)
        for claim in qualifying:
            relations_by_study[claim["Study_Title"]].add(claim["Evidence_Relation"])
        assigned = {
            study: min(relations, key=lambda relation: RELATION_ORDER[relation])
            for study, relations in relations_by_study.items()
        }
        for relation in ("Core", "Bridge", "Adjacent"):
            add(
                "Critical interfaces",
                measure,
                relation,
                "Study",
                sum(value == relation for value in assigned.values()),
                len(studies),
                definition,
            )

    for relation in ("Core", "Bridge", "Adjacent"):
        count = sum(claim["Evidence_Relation"] == relation for claim in claims)
        add("Evidence composition", "Evidence relation", relation, "Claim", count, len(claims), "Claim-level evidence relation")

    setting_labels = [
        ("Conceptual/formal", "Conceptual_Synthesis"),
        ("Offline", "Offline_Digital"),
        ("Simulation/HIL", "Closed_Loop_Simulation"),
        ("Controlled physical", "Controlled_Real_Robot"),
        ("Mixed", "Mixed_Settings"),
        ("Field", "Field_Deployment"),
    ]
    for label, value in setting_labels:
        count = sum(claim["Evidence_Setting"] == value for claim in claims)
        add("Evidence composition", "Evidence setting", label, "Claim", count, len(claims), value)

    recovery_count = sum(
        claim["Recovery_Level"] == "Verified_Safe_State_Recovery" for claim in claims
    )
    add(
        "Strict transition endpoint",
        "Verified safe-state recovery",
        "Core",
        "Claim",
        recovery_count,
        len(claims),
        "Recovery_Level equals Verified_Safe_State_Recovery",
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    if args.check:
        with AUDITED.open("r", encoding="utf-8-sig", newline="") as handle:
            audited = list(csv.DictReader(handle))
        normalized = [{key: str(value) for key, value in row.items()} for row in rows]
        if normalized != audited:
            for index, (left, right) in enumerate(zip(normalized, audited), start=1):
                if left != right:
                    raise ValueError(f"Mismatch at row {index}: reconstructed={left}; audited={right}")
            raise ValueError(f"Row-count mismatch: reconstructed={len(normalized)}; audited={len(audited)}")
        print(f"PASS: reconstructed {len(rows)} rows exactly match {AUDITED.name}.")
    else:
        print(f"Wrote {len(rows)} rows to {args.output}.")


if __name__ == "__main__":
    main()
