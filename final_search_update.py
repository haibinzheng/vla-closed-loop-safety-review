from __future__ import annotations

import csv
import html
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
PACKAGE_MODE = (HERE / "references.bib").exists()
ROOT = HERE.parents[0] if not PACKAGE_MODE else HERE
OUT = HERE if PACKAGE_MODE else ROOT / "01_PAPER" / "TEX4" / "supplement"
RAW = OUT / "search_raw"
OUT.mkdir(parents=True, exist_ok=True)
RAW.mkdir(parents=True, exist_ok=True)

SEARCH_START = "2026-07-29"
SEARCH_END = "2026-09-17"
EXECUTED_AT = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

FAMILIES = {
    "Failure_RQ1": [
        "safety", "attack", "backdoor", "perturbation", "distribution shift",
        "fault", "failure", "invalid handoff",
    ],
    "Observation_RQ2": [
        "uncertainty", "anomaly", "out-of-distribution", "monitoring",
        "calibration", "latency", "failure prediction",
    ],
    "Intervention_RQ3": [
        "rejection", "replanning", "filtering", "shielding", "arbitration",
        "fallback control", "switching", "emergency stop",
    ],
    "Transition_RQ4": [
        "correction", "retry", "resumption", "termination", "takeover",
        "recovery", "handback",
    ],
    "Assurance_RQ5": [
        "benchmark", "validation", "runtime assurance", "safety case",
        "evaluation protocol", "evidence", "reporting",
    ],
}

USER_AGENT = "VLA-closed-loop-review-final-search/1.0 (academic reproducibility update)"


def request_bytes(url: str, retries: int = 3) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except Exception as exc:  # preserve exact failure in the search log
            last = exc
            if attempt + 1 < retries:
                time.sleep(2 ** attempt)
    raise last


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    value = html.unescape(value)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def norm_title(value: str | None) -> str:
    value = clean_text(value).lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def norm_doi(value: str | None) -> str:
    if not value:
        return ""
    value = value.lower().strip()
    value = re.sub(r"^https?://(dx\.)?doi\.org/", "", value)
    return value


def norm_arxiv(value: str | None) -> str:
    if not value:
        return ""
    match = re.search(r"(?:arxiv:|/abs/)?(\d{4}\.\d{4,5})(?:v\d+)?", value, re.I)
    return match.group(1) if match else ""


def first_date(*values: str | None) -> str:
    for value in values:
        if value:
            return str(value)[:10]
    return ""


def read_existing_keys():
    files = ([
        HERE / "traceability_study_registry.csv",
        HERE / "status_closed_claims.csv",
    ] if PACKAGE_MODE else [
        ROOT / "02_EVIDENCE" / "round2_formal" / "study_registry.csv",
        ROOT / "02_EVIDENCE" / "closed_claims" / "status_closed_claims.csv",
    ])
    dois, arxivs, titles = set(), set(), set()
    for path in files:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                for key in ("DOI", "doi"):
                    if row.get(key):
                        dois.add(norm_doi(row[key]))
                for key in ("arXiv_ID", "arxiv_id", "ArXiv_ID"):
                    if row.get(key):
                        arxivs.add(norm_arxiv(row[key]))
                for key in ("Canonical_Title", "Title", "title", "Paper_Title"):
                    if row.get(key):
                        titles.add(norm_title(row[key]))
    return dois, arxivs, titles


def arxiv_query(family: str, terms: list[str]):
    term_block = " OR ".join(f'\"{t}\"' if " " in t else t for t in terms)
    query = (
        f'submittedDate:[{SEARCH_START.replace("-", "")}0000 TO '
        f'{SEARCH_END.replace("-", "")}2359] AND '
        f'all:\"vision-language-action\" AND all:({term_block})'
    )
    params = urllib.parse.urlencode({
        "search_query": query,
        "start": 0,
        "max_results": 1000,
        "sortBy": "submittedDate",
        "sortOrder": "ascending",
    })
    url = f"https://export.arxiv.org/api/query?{params}"
    raw = request_bytes(url)
    (RAW / f"arxiv_{family}.xml").write_bytes(raw)
    root = ET.fromstring(raw)
    atom = {"a": "http://www.w3.org/2005/Atom", "o": "http://a9.com/-/spec/opensearch/1.1/"}
    total = int(root.findtext("o:totalResults", default="0", namespaces=atom))
    rows = []
    for entry in root.findall("a:entry", atom):
        identifier = entry.findtext("a:id", default="", namespaces=atom)
        authors = [clean_text(x.findtext("a:name", default="", namespaces=atom)) for x in entry.findall("a:author", atom)]
        rows.append({
            "source": "arXiv",
            "family": family,
            "source_id": norm_arxiv(identifier),
            "doi": norm_doi(entry.findtext("a:doi", default="", namespaces={**atom, "a": "http://www.w3.org/2005/Atom"})),
            "arxiv_id": norm_arxiv(identifier),
            "title": clean_text(entry.findtext("a:title", default="", namespaces=atom)),
            "abstract": clean_text(entry.findtext("a:summary", default="", namespaces=atom)),
            "authors": "; ".join(authors),
            "published_date": first_date(entry.findtext("a:published", default="", namespaces=atom)),
            "updated_date": first_date(entry.findtext("a:updated", default="", namespaces=atom)),
            "url": identifier,
        })
    return query, url, total, rows


def openalex_query(family: str, terms: list[str]):
    search = '"vision-language-action" ' + " OR ".join(f'"{t}"' if " " in t else t for t in terms)
    cursor = "*"
    rows = []
    raw_pages = []
    total = 0
    while cursor and len(rows) < 2000:
        params = urllib.parse.urlencode({
            "search": search,
            "filter": f"from_publication_date:{SEARCH_START},to_publication_date:{SEARCH_END}",
            "per-page": 200,
            "cursor": cursor,
        })
        url = f"https://api.openalex.org/works?{params}"
        page = json.loads(request_bytes(url))
        raw_pages.append(page)
        total = int(page.get("meta", {}).get("count", 0))
        for item in page.get("results", []):
            abstract_index = item.get("abstract_inverted_index") or {}
            words = []
            for word, positions in abstract_index.items():
                for pos in positions:
                    words.append((pos, word))
            abstract = " ".join(word for _, word in sorted(words))
            authors = [x.get("author", {}).get("display_name", "") for x in item.get("authorships", [])]
            ids = item.get("ids") or {}
            primary = item.get("primary_location") or {}
            source = primary.get("source") or {}
            rows.append({
                "source": "OpenAlex",
                "family": family,
                "source_id": item.get("id", ""),
                "doi": norm_doi(item.get("doi") or ids.get("doi")),
                "arxiv_id": norm_arxiv(ids.get("arxiv") or primary.get("landing_page_url")),
                "title": clean_text(item.get("display_name") or item.get("title")),
                "abstract": clean_text(abstract),
                "authors": "; ".join(a for a in authors if a),
                "published_date": first_date(item.get("publication_date")),
                "updated_date": "",
                "url": item.get("doi") or primary.get("landing_page_url") or item.get("id", ""),
                "venue": source.get("display_name", ""),
                "work_type": item.get("type", ""),
                "is_retracted": bool(item.get("is_retracted")),
            })
        next_cursor = page.get("meta", {}).get("next_cursor")
        if not next_cursor or not page.get("results"):
            break
        cursor = next_cursor
        time.sleep(0.15)
    (RAW / f"openalex_{family}.json").write_text(json.dumps(raw_pages, ensure_ascii=False), encoding="utf-8")
    return search, url, total, rows


def crossref_query(family: str, terms: list[str]):
    query = '"vision-language-action" ' + " OR ".join(f'"{t}"' if " " in t else t for t in terms)
    params = urllib.parse.urlencode({
        "query.bibliographic": query,
        "filter": f"from-pub-date:{SEARCH_START},until-pub-date:{SEARCH_END}",
        "rows": 1000,
        "select": "DOI,title,author,abstract,published-online,published-print,URL,publisher,container-title,type,update-to",
    })
    url = f"https://api.crossref.org/works?{params}"
    page = json.loads(request_bytes(url))
    (RAW / f"crossref_{family}.json").write_text(json.dumps(page, ensure_ascii=False), encoding="utf-8")
    message = page.get("message", {})
    total = int(message.get("total-results", 0))
    rows = []
    for item in message.get("items", []):
        authors = []
        for author in item.get("author", []):
            authors.append(" ".join(x for x in [author.get("given", ""), author.get("family", "")] if x))
        date_parts = (item.get("published-online") or item.get("published-print") or {}).get("date-parts", [[]])[0]
        date = "-".join(str(x).zfill(2) for x in date_parts) if date_parts else ""
        title = item.get("title") or []
        container = item.get("container-title") or []
        rows.append({
            "source": "Crossref",
            "family": family,
            "source_id": item.get("DOI", ""),
            "doi": norm_doi(item.get("DOI")),
            "arxiv_id": norm_arxiv(item.get("URL")),
            "title": clean_text(title[0] if title else ""),
            "abstract": clean_text(item.get("abstract", "")),
            "authors": "; ".join(authors),
            "published_date": date,
            "updated_date": "",
            "url": item.get("URL", ""),
            "venue": container[0] if container else item.get("publisher", ""),
            "work_type": item.get("type", ""),
            "is_retracted": bool(item.get("update-to")),
        })
    return query, url, total, rows


def evidence_priority(title: str, abstract: str):
    text = f"{title} {abstract}".lower()
    vla = bool(re.search(r"vision[\s\-–]language[\s\-–]action|\bvla\b", text))
    embodied = bool(re.search(r"robot|robotic|embodied|autonomous driv|navigation|manipulat|aerial|uav|vehicle", text))
    safety = bool(re.search(r"safety|safe |attack|backdoor|fault|failure|risk|uncertaint|anomal|out.of.distribution|monitor|shield|fallback|recovery|takeover|handback|emergency|robust", text))
    operational = bool(re.search(r"action|execution|control|policy|trajectory|actuation|intervention|replan|terminate|switch", text))
    if vla and safety:
        return "P1_Direct_VLA_Safety", "Direct VLA term plus a safety, failure, monitoring, intervention, or recovery concept."
    if embodied and safety and operational:
        return "P2_Operational_Bridge", "Embodied system plus safety concept and an explicit action/control interface."
    if safety and operational:
        return "P3_Adjacent_Context", "Safety-relevant operational method without an explicit VLA or embodied-system bridge in metadata."
    return "Not_Prioritized", "Metadata lacks the joint embodied-action and safety/interface signal required for full-text priority."


existing_dois, existing_arxivs, existing_titles = read_existing_keys()
query_log = []
records = []

for family, terms in FAMILIES.items():
    for source, fn in (("arXiv", arxiv_query), ("OpenAlex", openalex_query), ("Crossref", crossref_query)):
        started = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        try:
            query, url, total, rows = fn(family, terms)
            status, note = "Executed", "Public endpoint completed; normalized records retained with raw response."
            records.extend(rows)
            retrieved = len(rows)
        except Exception as exc:
            query = '"vision-language-action" AND (' + " OR ".join(terms) + ")"
            url, total, retrieved, status = "", "", 0, "Failed"
            note = f"{type(exc).__name__}: {exc}"
        query_log.append({
            "executed_at_utc": started,
            "search_window_start": SEARCH_START,
            "search_window_end": SEARCH_END,
            "source": source,
            "family": family,
            "exact_query": query,
            "returned_count": total,
            "retrieved_count": retrieved,
            "status": status,
            "endpoint": url,
            "note": note,
        })
        time.sleep(0.35)


grouped = {}
for row in records:
    doi = norm_doi(row.get("doi"))
    arxiv = norm_arxiv(row.get("arxiv_id"))
    title_key = norm_title(row.get("title"))
    key = f"doi:{doi}" if doi else (f"arxiv:{arxiv}" if arxiv else f"title:{title_key}")
    if not title_key:
        continue
    if key not in grouped:
        grouped[key] = dict(row)
        grouped[key]["sources"] = set()
        grouped[key]["families"] = set()
    g = grouped[key]
    g["sources"].add(row.get("source", ""))
    g["families"].add(row.get("family", ""))
    for field in ("doi", "arxiv_id", "abstract", "authors", "venue", "work_type", "url", "published_date", "updated_date"):
        if not g.get(field) and row.get(field):
            g[field] = row[field]
    g["is_retracted"] = bool(g.get("is_retracted") or row.get("is_retracted"))


deduped = []
for i, (key, row) in enumerate(sorted(grouped.items(), key=lambda kv: (kv[1].get("published_date", ""), norm_title(kv[1].get("title")))), 1):
    doi = norm_doi(row.get("doi"))
    arxiv = norm_arxiv(row.get("arxiv_id"))
    title_key = norm_title(row.get("title"))
    existing_match = ""
    if doi and doi in existing_dois:
        existing_match = "DOI"
    elif arxiv and arxiv in existing_arxivs:
        existing_match = "arXiv_ID"
    elif title_key in existing_titles:
        existing_match = "Normalized_Title"
    priority, reason = evidence_priority(row.get("title", ""), row.get("abstract", ""))
    if row.get("is_retracted"):
        disposition = "Exclude_Retracted_or_Updated"
    elif existing_match:
        disposition = "Existing_Corpus_Update_Check"
    elif priority.startswith("P1"):
        disposition = "New_Full_Text_Priority"
    elif priority.startswith("P2"):
        disposition = "New_Metadata_Screen"
    elif priority.startswith("P3"):
        disposition = "Contextual_Metadata"
    else:
        disposition = "Not_Prioritized"
    deduped.append({
        "update_record_id": f"FSU-{i:04d}",
        "dedup_key": key,
        "title": row.get("title", ""),
        "authors": row.get("authors", ""),
        "published_date": row.get("published_date", ""),
        "updated_date": row.get("updated_date", ""),
        "doi": doi,
        "arxiv_id": arxiv,
        "venue": row.get("venue", ""),
        "work_type": row.get("work_type", ""),
        "sources": ";".join(sorted(x for x in row["sources"] if x)),
        "families": ";".join(sorted(x for x in row["families"] if x)),
        "abstract": row.get("abstract", ""),
        "url": row.get("url", ""),
        "existing_corpus_match": existing_match,
        "priority_class": priority,
        "priority_reason": reason,
        "screening_disposition": disposition,
        "retraction_or_update_flag": "Yes" if row.get("is_retracted") else "No",
    })


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


write_csv(OUT / "final_search_log.csv", query_log)
write_csv(OUT / "final_search_records.csv", deduped)

summary = {
    "executed_at_utc": EXECUTED_AT,
    "window": {"start": SEARCH_START, "end": SEARCH_END},
    "query_operations": len(query_log),
    "successful_operations": sum(x["status"] == "Executed" for x in query_log),
    "failed_operations": sum(x["status"] != "Executed" for x in query_log),
    "normalized_source_rows": len(records),
    "deduplicated_records": len(deduped),
    "existing_corpus_matches": sum(bool(x["existing_corpus_match"]) for x in deduped),
    "new_full_text_priority": sum(x["screening_disposition"] == "New_Full_Text_Priority" for x in deduped),
    "new_metadata_screen": sum(x["screening_disposition"] == "New_Metadata_Screen" for x in deduped),
    "contextual_metadata": sum(x["screening_disposition"] == "Contextual_Metadata" for x in deduped),
    "not_prioritized": sum(x["screening_disposition"] == "Not_Prioritized" for x in deduped),
    "retracted_or_updated": sum(x["screening_disposition"] == "Exclude_Retracted_or_Updated" for x in deduped),
    "disposition_counts": dict(sorted((k, len(v)) for k, v in defaultdict(list, {
        key: [x for x in deduped if x["screening_disposition"] == key]
        for key in set(x["screening_disposition"] for x in deduped)
    }).items())),
}
(OUT / "final_search_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(summary, indent=2, ensure_ascii=False))
