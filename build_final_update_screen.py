from __future__ import annotations

import csv
import re
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
PACKAGE_MODE = (HERE / "final_search_records.csv").exists()
ROOT = HERE.parents[0] if not PACKAGE_MODE else HERE
SUPP = HERE if PACKAGE_MODE else ROOT / "01_PAPER" / "TEX4" / "supplement"
SOURCE = SUPP / "final_search_records.csv"
OUT = SUPP / ("reconstructed_preliminary_screen.csv" if PACKAGE_MODE else "final_update_screen.csv")
PDF_DIR = (SUPP / "fulltext") if PACKAGE_MODE else ROOT / "03_SOURCES" / "fulltext_intake" / "final_update"
PDF_DIR.mkdir(parents=True, exist_ok=True)

FULL_TEXT = {
    "2607.26789": "Execution-time verification, intervention, and repair may inform RQ2--RQ4.",
    "2607.27881": "Runtime monitoring, hierarchical recovery, and real-world orchestration may inform RQ2--RQ4.",
    "2608.00315": "Language-conditioned latent safety filtering may inform RQ3.",
    "2608.03207": "Adversarial patch attack against flow-matching VLAs may inform RQ1.",
    "2608.04510": "Uncertainty and ablation-based risk detection may inform RQ2.",
    "2608.04692": "Closed-loop target-and-control audit may inform RQ3 and RQ5.",
    "2608.13474": "Runtime-readable task progress may inform RQ2 and transition verification.",
    "2608.16697": "Self-evaluated action uncertainty may inform RQ2.",
    "2608.17095": "Inference-time steering in driving requires full-text safety-boundary assessment.",
    "2608.17496": "Predictive safety and model-based shielding may inform RQ2, RQ3, and RQ5.",
    "2608.17717": "Formal preservation of multimodal intent may inform RQ3 and RQ5.",
    "2608.20556": "Temporal-logic-conditioned action generation may inform RQ3 and RQ5.",
    "2608.25757": "Progress, event, and uncertainty prediction may inform RQ2.",
    "2608.26645": "Autonomous correction and recovery may inform RQ3 and RQ4.",
    "2609.05178": "Failure-recovery benchmark may inform RQ4 and RQ5.",
    "2609.09250": "Verifier survey is a directly overlapping review for positioning and RQ5.",
    "2609.11697": "Constraint enforcement for flow-matching policies may inform RQ3 and RQ5.",
    "2609.12371": "Risk-informed driving control requires full-text interface assessment.",
    "2609.15005": "Cross-layer propagation attribution may inform RQ1 and RQ5.",
    "2607.27782": "Failure-driven action correction may inform RQ1, RQ3, and RQ4.",
    "2607.27933": "Runtime uncertainty and failure detection may inform RQ2.",
    "2607.29169": "Runtime detection, mitigation, and resumption may connect RQ2--RQ4.",
    "2607.29569": "Barrier-constrained action generation may inform RQ3 and assurance boundaries.",
    "2608.04246": "Calibrated deployment-shift failure detection may inform RQ2 and RQ5.",
    "2608.03231": "Physical attack and defense evidence may inform RQ1 and RQ3.",
    "2608.10393": "Physical-world adversarial attack evidence may inform RQ1.",
    "2608.13395": "Failure-informed policy update requires full-text boundary assessment.",
    "2608.13453": "Cross-task physical adversarial texture evidence may inform RQ1.",
    "2608.14822": "Inference-time recovery may inform RQ3 and RQ4.",
    "2608.15475": "Deployed weight-fault attack evidence may inform RQ1.",
    "2608.17600": "Authorized versus unauthorized visual-cue benchmark may inform RQ1 and RQ5.",
    "2608.20791": "Closed-loop certificate and defense may inform RQ2, RQ3, and RQ5.",
    "2608.26578": "Configured failure-mode backdoor evidence may inform RQ1.",
    "2608.29583": "Reasoning--trajectory consistency monitor may inform RQ2.",
    "2608.29967": "Action correction and recovery evidence may inform RQ3 and RQ4.",
    "2609.03142": "Sensor-evidence gating requires full-text assessment of safety relevance.",
    "2609.13231": "Reachability-informed safety alignment may inform RQ3 and RQ5.",
    "2609.04277": "Timestamp-level failure detection may inform RQ2.",
    "2609.05832": "Force-aware reactive control may inform timing and execution evidence.",
    "2609.06114": "Failure-boundary learning requires full-text assessment of runtime transfer.",
    "2609.06508": "Closed-loop verification and recovery may inform RQ2--RQ4.",
    "2609.15940": "Compound robustness evaluation may inform RQ5.",
    "2609.11445": "Online failure monitoring from frozen world-model states may inform RQ2 and RQ5.",
    "2609.13236": "Post-deployment adaptation and safety governance may inform RQ5.",
}

METADATA_EXCLUDE = {
    "2608.01755": "VLM-only reasoning supervision and verification without an embodied execution path.",
    "2608.08904": "Representation probing of depth decodability without a runtime safety endpoint.",
    "2608.09467": "Failure-aware policy training for task success without a declared safety endpoint.",
    "2608.10413": "Failure-memory training for driving performance without a declared runtime safety endpoint.",
    "2608.14028": "Domain-adversarial representation learning for task generalization rather than safety assurance.",
    "2608.02497": "Instruction generalization and task performance without a declared safety endpoint.",
    "2608.06965": "Camera-view task robustness without a declared safety endpoint.",
    "2608.22419": "Training robustness and task success without a declared safety endpoint.",
    "2608.25308": "Representation recovery for task performance rather than post-failure recovery.",
    "2608.15636": "Inference efficiency; verification concerns speculative computation rather than safety monitoring.",
    "2609.06256": "Hybrid manipulation robustness without a declared safety endpoint in metadata.",
}

DOI_FULL_TEXT = {
    "10.5281/zenodo.21786583": "Safety-gated lifecycle framework may inform RQ3 and RQ5.",
    "10.5281/zenodo.21965132": "Self-verification and correction may inform RQ2--RQ4.",
    "10.3390/e28090975": "OOD input-stream diagnosis and training-free correction may inform RQ1 and RQ3.",
    "10.21203/rs.3.rs-10909571/v1": "Safety-knowledge retrieval for driving requires full-text assessment.",
}

DOI_EXCLUDE = {
    "10.7470/jkst.2026.44.4.722": "VLM-only driving-risk understanding benchmark without an embodied action path.",
    "10.1016/j.jafr.2026.103286": "Task-progress monitoring without a declared safety property or safety endpoint.",
    "10.31181/dma412026180": "Data retargeting and task robustness without a declared safety endpoint.",
}


def norm_title(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()


def contains_vla(value: str) -> bool:
    return bool(re.search(r"vision[\s\-–]language[\s\-–]action|\bvla\b", value, re.I))


def strong_title(value: str) -> bool:
    safety = re.search(
        r"safe|safety|attack|backdoor|fault|failure|risk|uncertain|anomal|out.of.distribution|"
        r"monitor|verif|shield|fallback|recover|takeover|handback|emergency|robust|adversarial|jailbreak|poison",
        value,
        re.I,
    )
    return bool(safety)


def is_priority(row: dict[str, str]) -> bool:
    """Route every exact-VLA record to one mutually exclusive final-update stratum."""
    arxiv = row.get("arxiv_id", "")
    doi = row.get("doi", "").lower()
    explicit = (
        arxiv in FULL_TEXT
        or arxiv in METADATA_EXCLUDE
        or doi in DOI_FULL_TEXT
        or doi in DOI_EXCLUDE
        or bool(row.get("existing_corpus_match"))
    )
    return contains_vla(f"{row.get('title', '')} {row.get('abstract', '')}") and (
        strong_title(row.get("title", "")) or explicit
    )


with SOURCE.open("r", encoding="utf-8-sig", newline="") as handle:
    source_rows = list(csv.DictReader(handle))

selected = {}
for row in source_rows:
    if not is_priority(row):
        continue
    key = norm_title(row["title"])
    current = selected.get(key)
    # Prefer an arXiv-bearing row and preserve an existing-corpus match if present.
    if current is None or (not current.get("arxiv_id") and row.get("arxiv_id")):
        selected[key] = row
    elif row.get("existing_corpus_match") and not current.get("existing_corpus_match"):
        selected[key] = row

screen = []
for i, row in enumerate(sorted(selected.values(), key=lambda x: (x["published_date"], x["title"])), 1):
    arxiv = row.get("arxiv_id", "")
    doi = row.get("doi", "").lower()
    if row.get("existing_corpus_match"):
        decision = "Existing_Corpus_Update_Check"
        reason = "Matched an existing study identity; verify version and publication metadata only."
    elif arxiv in FULL_TEXT:
        decision = "Retrieve_Full_Text"
        reason = FULL_TEXT[arxiv]
    elif doi in DOI_FULL_TEXT:
        decision = "Retrieve_Full_Text"
        reason = DOI_FULL_TEXT[doi]
    elif arxiv in METADATA_EXCLUDE:
        decision = "Exclude_After_Metadata_Screen"
        reason = METADATA_EXCLUDE[arxiv]
    elif doi in DOI_EXCLUDE:
        decision = "Exclude_After_Metadata_Screen"
        reason = DOI_EXCLUDE[doi]
    else:
        decision = "Retrieve_Full_Text"
        reason = "Safety-relevant title; full text required to apply the RQ-linked eligibility criteria."
    pdf_path = ""
    if arxiv and decision == "Retrieve_Full_Text":
        pdf_path = str((PDF_DIR / f"{arxiv}.pdf").relative_to(ROOT)).replace("\\", "/")
    screen.append({
        "screen_id": f"FSU-S-{i:03d}",
        "update_record_id": row["update_record_id"],
        "title": row["title"],
        "published_date": row["published_date"],
        "authors": row["authors"],
        "doi": doi,
        "arxiv_id": arxiv,
        "sources": row["sources"],
        "initial_screen_decision": decision,
        "initial_screen_reason": reason,
        "full_text_path": pdf_path,
        "full_text_status": "Pending" if decision == "Retrieve_Full_Text" else "Not_Applicable",
        "eligibility_decision": "Pending" if decision == "Retrieve_Full_Text" else decision,
        "eligibility_reason": "",
    })

with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(screen[0].keys()))
    writer.writeheader()
    writer.writerows(screen)

print(f"screen_rows={len(screen)}")
print(f"retrieve_full_text={sum(x['initial_screen_decision'] == 'Retrieve_Full_Text' for x in screen)}")
print(f"metadata_excluded={sum(x['initial_screen_decision'] == 'Exclude_After_Metadata_Screen' for x in screen)}")
print(f"existing_update_checks={sum(x['initial_screen_decision'] == 'Existing_Corpus_Update_Check' for x in screen)}")
