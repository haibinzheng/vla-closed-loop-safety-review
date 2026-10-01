#!/usr/bin/env python3
"""Merge the complete priority route with the audited final-update decisions.

The routing reconstruction is intentionally separate from the frozen claim corpus.
Existing audited decisions are preserved by normalized title. Newly recovered records
receive the source and eligibility decisions documented below.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRELIMINARY = HERE / "reconstructed_preliminary_screen.csv"
FINAL = HERE / "final_update_screen.csv"

INCLUDE_HTML = {"2607.26789", "2607.27881", "2609.11445", "2609.13236"}
SOURCE_DEFERRED_DOI = {"10.5281/zenodo.21786583", "10.5281/zenodo.21965132"}


def norm_title(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()


with FINAL.open("r", encoding="utf-8-sig", newline="") as handle:
    old_rows = list(csv.DictReader(handle))
old_by_title = {norm_title(row["title"]): row for row in old_rows}

with PRELIMINARY.open("r", encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle))

for row in rows:
    old = old_by_title.get(norm_title(row["title"]))
    if old:
        for field in ("full_text_status", "eligibility_decision", "eligibility_reason"):
            row[field] = old[field]
        continue

    arxiv = row.get("arxiv_id", "")
    doi = row.get("doi", "").lower()
    if arxiv in INCLUDE_HTML:
        row["full_text_status"] = "Authoritative_HTML_Checked"
        row["eligibility_decision"] = "Include_Late_Update_Sensitivity"
        row["eligibility_reason"] = (
            "Meets at least one RQ-linked eligibility criterion; retained outside "
            "the frozen 254-claim descriptive counts."
        )
    elif doi in SOURCE_DEFERRED_DOI:
        row["full_text_status"] = "Source_Deferred"
        row["eligibility_decision"] = "Source_Deferred"
        row["eligibility_reason"] = (
            "Authoritative full text was not obtained; no eligibility or effect claim is made."
        )

with FINAL.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"final_update_records={len(rows)}")
print(f"newly_routed_records={len(rows) - len(old_rows)}")
