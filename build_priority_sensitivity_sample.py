from __future__ import annotations

import csv
import random
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
PACKAGE_MODE = (HERE / "final_search_records.csv").exists()
ROOT = HERE.parents[0] if not PACKAGE_MODE else HERE
SUPP = HERE if PACKAGE_MODE else ROOT / "01_PAPER" / "TEX4" / "supplement"
RECORDS = SUPP / "final_search_records.csv"
OUT = SUPP / "final_update_priority_sensitivity_sample.csv"
SEED = 62406286


def key(title: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", title.lower())).strip()


vla = re.compile(r"vision[\s\-–]language[\s\-–]action|\bvla\b", re.I)
strong = re.compile(
    r"safe|safety|attack|backdoor|fault|failure|risk|uncertain|anomal|out.of.distribution|"
    r"monitor|verif|shield|fallback|recover|takeover|handback|emergency|robust|adversarial|jailbreak|poison",
    re.I,
)

PRIORITY_ARXIV = {
    "2607.26789", "2607.27782", "2607.27881", "2607.27933", "2607.29169", "2607.29569",
    "2608.00315", "2608.01755", "2608.02497", "2608.03207", "2608.03231", "2608.04246",
    "2608.04510", "2608.04692", "2608.06965", "2608.08904", "2608.09467", "2608.10393",
    "2608.10413", "2608.13395", "2608.13453", "2608.13474", "2608.14028", "2608.14822",
    "2608.15475", "2608.15636", "2608.16697", "2608.17095", "2608.17496", "2608.17600",
    "2608.17717", "2608.20556", "2608.20791", "2608.22419", "2608.25308", "2608.25757",
    "2608.26578", "2608.26645", "2608.29583", "2608.29967", "2609.03142", "2609.04277",
    "2609.05178", "2609.05832", "2609.06114", "2609.06256", "2609.06508", "2609.09250",
    "2609.11445", "2609.11697", "2609.12371", "2609.13231", "2609.13236", "2609.15005",
    "2609.15940",
}
PRIORITY_DOI = {
    "10.21203/rs.3.rs-10909571/v1", "10.31181/dma412026180", "10.3390/e28090975",
    "10.5281/zenodo.21786583", "10.5281/zenodo.21965132", "10.7470/jkst.2026.44.4.722",
    "10.1016/j.jafr.2026.103286",
}


def is_priority(row: dict[str, str]) -> bool:
    return bool(
        strong.search(row["title"])
        or row.get("arxiv_id", "") in PRIORITY_ARXIV
        or row.get("doi", "").lower() in PRIORITY_DOI
        or row.get("existing_corpus_match")
    )

with RECORDS.open("r", encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle))
unique = {}
for row in rows:
    title_key = key(row["title"])
    if title_key and vla.search(f"{row['title']} {row['abstract']}") and title_key not in unique:
        unique[title_key] = row

priority = [row for row in unique.values() if is_priority(row)]
pool = [row for row in unique.values() if not is_priority(row)]
assert len(priority) + len(pool) == len(unique)
assert not ({key(row["title"]) for row in priority} & {key(row["title"]) for row in pool})
random.Random(SEED).shuffle(pool)
sample = pool[:30]

promoted = {
    "Decoding Task Progress from VLA Representations",
    "CompCPZ: Preserving Multi-Modal Intent in Language-Guided Robot Manipulation",
}
contextual = {
    "Applications of Reinforcement Learning for Autonomous Surgical Robotics: A Systematic Review",
    "From Language to Action: Survey of LLM-Driven Robotic Manipulation Paradigms",
    "World-Action Models for Robot Learning and Control: A Survey",
}

out = []
for index, row in enumerate(sample, 1):
    if row["title"] in promoted:
        decision = "Promoted_to_Full_Text"
        reason = "Metadata exposed a direct runtime-monitoring or formal execution interface omitted by the title-only rule."
    elif row["title"] in contextual:
        decision = "Contextual_Review"
        reason = "Review-level context without new primary same-system closed-loop evidence for the frozen synthesis."
    else:
        decision = "No_Promotion"
        reason = "Task capability, efficiency, representation, training, or generalization study without an explicit safety-monitoring, authority, recovery, or assurance endpoint in the metadata."
    out.append({
        "sample_order": index,
        "random_seed": SEED,
        "title": row["title"],
        "published_date": row["published_date"],
        "doi": row["doi"],
        "arxiv_id": row["arxiv_id"],
        "decision": decision,
        "reason": reason,
    })

with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(out[0].keys()))
    writer.writeheader()
    writer.writerows(out)

print(f"exact_vla_unique={len(unique)}")
print(f"priority_pool={len(priority)}")
print(f"nonpriority_pool={len(pool)}")
print(f"sample={len(out)}")
print(f"promoted={sum(x['decision'] == 'Promoted_to_Full_Text' for x in out)}")
