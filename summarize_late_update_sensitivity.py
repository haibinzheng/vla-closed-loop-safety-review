#!/usr/bin/env python3
"""Summarize the existing study-level late-update sensitivity mapping.

This script does not create claim-level codes. It counts the author-verified
evidence-relation and observed-link fields already stored in
final_update_qualitative_synthesis.csv. Node-pair counts denote study-level
co-occurrence, not an experimentally verified interface connection.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "final_update_qualitative_synthesis.csv"
OUTPUT = ROOT / "late_update_structured_counts.csv"

ORDERED_NODES = (
    "origin",
    "propagation",
    "signal",
    "verdict",
    "authority",
    "response",
    "execution",
    "outcome",
    "transition",
    "property",
)

CONNECTIONS = (
    ("verdict", "authority"),
    ("authority", "response"),
    ("response", "execution"),
    ("execution", "outcome"),
    ("execution", "transition"),
)

ALLOWED_RELATIONS = {"Core", "Bridge", "Adjacent"}
ALLOWED_AUXILIARY_LABELS = {
    "evaluation",
    "failure",
    "representation",
    "risk",
    "timing",
    "validation",
}
ALLOWED_NODES = set(ORDERED_NODES) | ALLOWED_AUXILIARY_LABELS

NONEXCLUSIVE_SCOPE = (
    "Existing study-level late-update sensitivity mapping; node and node-pair counts "
    "are non-mutually-exclusive; not claim-level recoding and not part of frozen "
    "quantitative denominators."
)
RELATION_SCOPE = (
    "Existing study-level late-update sensitivity mapping; evidence relations are "
    "mutually exclusive; not claim-level recoding and not part of frozen quantitative "
    "denominators."
)
VALIDATION_SCOPE = (
    "Existing study-level late-update sensitivity mapping; one row per retained study; "
    "not claim-level recoding and not part of frozen quantitative denominators."
)


def main() -> None:
    with INPUT.open("r", encoding="utf-8-sig", newline="") as handle:
        studies = list(csv.DictReader(handle))

    invalid_relations = sorted(
        {row["evidence_relation"].strip() for row in studies} - ALLOWED_RELATIONS
    )
    if invalid_relations:
        raise ValueError(f"Unexpected evidence_relation values: {invalid_relations}")

    relation_counts = Counter(row["evidence_relation"].strip() for row in studies)
    link_lists = [
        [token.strip() for token in row["observed_links"].split("-") if token.strip()]
        for row in studies
    ]
    invalid_nodes = sorted({node for links in link_lists for node in links} - ALLOWED_NODES)
    if invalid_nodes:
        raise ValueError(f"Unexpected observed_links labels: {invalid_nodes}")
    node_counts = Counter(node for links in link_lists for node in set(links))

    output_rows: list[dict[str, object]] = []

    def add(summary_type: str, item: str, count: int, scope: str, note: str) -> None:
        output_rows.append(
            {
                "summary_type": summary_type,
                "item": item,
                "count": count,
                "denominator": len(studies),
                "scope": scope,
                "note": note,
            }
        )

    add(
        "validation",
        "eligible_late_update_studies",
        len(studies),
        VALIDATION_SCOPE,
        "One row per retained study.",
    )
    for relation in ("Core", "Bridge", "Adjacent"):
        add(
            "evidence_relation",
            relation,
            relation_counts[relation],
            RELATION_SCOPE,
            "Mutually exclusive study relation.",
        )
    for node in ORDERED_NODES:
        if node_counts[node]:
            add(
                "observed_node",
                node,
                node_counts[node],
                NONEXCLUSIVE_SCOPE,
                "Node appears in the study-level observed_links field.",
            )
    for left, right in CONNECTIONS:
        count = sum(left in links and right in links for links in link_lists)
        add(
            "node_cooccurrence_pattern",
            f"{left}_and_{right}",
            count,
            NONEXCLUSIVE_SCOPE,
            "Both nodes occur in the study-level mapping; adjacency, same-run connection, and causality are not inferred.",
        )

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_rows[0].keys())
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Wrote {len(output_rows)} rows to {OUTPUT.name} from {len(studies)} studies.")


if __name__ == "__main__":
    main()
