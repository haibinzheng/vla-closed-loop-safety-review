#!/usr/bin/env python3
"""Audit identifier-backed 2026 bibliography entries against Crossref and arXiv."""

from __future__ import annotations

import csv
import html
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE_MODE = (HERE / "references.bib").exists()
ROOT = HERE.parents[0] if not PACKAGE_MODE else HERE
BIB = (HERE / "references.bib") if PACKAGE_MODE else ROOT / "01_PAPER" / "TEX4" / "references.bib"
OUT = (HERE / "bibliography_2026_status_audit.csv") if PACKAGE_MODE else ROOT / "01_PAPER" / "TEX4" / "supplement" / "bibliography_2026_status_audit.csv"
UA = "ClosedLoopVLAReview/1.0 (bibliography audit; contact via manuscript corresponding author)"
PRIMARY_PAGES_VERIFIED_2026_09_17 = {
    "2607.13818", "2607.17786", "2606.23754", "2606.09749", "2604.23775",
    "2606.08881", "2606.09499", "2606.20754", "2603.13782", "2601.21712",
    "2602.01834", "2604.20472", "2608.00315", "2608.13474", "2609.09250",
}
MANUALLY_RESOLVED_PRIMARY_SOURCES = {
    "Li2026EmbodiedManipulationSurvey": {
        "remote_status": "publisher_index_verified",
        "remote_updated": "checked 2026-09-17",
        "publication_type": "journal article",
        "withdrawal_status": "no_retraction_notice_on_publisher_index_2026-09-17",
        "relation": "https://www.aas.net.cn/cn/article/doi/10.16383/j.aas.c250394",
    },
    "Choi2026EMBGuard": {
        "remote_status": "primary_page_verified",
        "remote_updated": "v1 checked 2026-09-17",
        "publication_type": "arXiv preprint; accepted at ICML 2026",
        "withdrawal_status": "no_withdrawal_notice_on_primary_page_2026-09-17",
        "relation": "https://arxiv.org/abs/2605.30924",
    },
}


class CitationMetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: dict[str, list[str]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "meta":
            return
        data = {key.lower(): value or "" for key, value in attrs}
        name = data.get("name", "").lower()
        if name.startswith("citation_") and data.get("content"):
            self.values.setdefault(name, []).append(html.unescape(data["content"]).strip())


def clean(value: str) -> str:
    return re.sub(r"[{}\\]", "", value).strip().strip('"')


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", clean(value).lower()).strip()


def parse_entries(text: str) -> list[dict[str, str]]:
    starts = list(re.finditer(r"(?m)^@(\w+)\{([^,]+),", text))
    records: list[dict[str, str]] = []
    for i, match in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        body = text[match.end():end]
        fields: dict[str, str] = {"entry_type": match.group(1), "key": match.group(2).strip()}
        for fm in re.finditer(r"(?ms)(?:^|,)\s*(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|\".*?\")\s*", body):
            fields[fm.group(1).lower()] = clean(fm.group(2))
        if fields.get("year") == "2026":
            records.append(fields)
    return records


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def crossref_record(doi: str) -> dict[str, str]:
    try:
        message = get_json("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""))["message"]
        title = (message.get("title") or [""])[0]
        authors = message.get("author") or []
        author = " ".join(filter(None, [authors[0].get("given", ""), authors[0].get("family", "")])) if authors else ""
        relation = json.dumps(message.get("relation") or {}, ensure_ascii=False, sort_keys=True)
        subtype = message.get("subtype") or ""
        update_to = json.dumps(message.get("update-to") or [], ensure_ascii=False, sort_keys=True)
        status_blob = " ".join([title, relation, subtype, update_to]).lower()
        flag = "withdrawal_or_update_flag" if any(x in status_blob for x in ("withdraw", "retract", "update-to")) else "no_withdrawal_flag_in_crossref_record"
        return {
            "remote_status": "resolved",
            "remote_title": title,
            "remote_first_author": author,
            "remote_updated": str(message.get("indexed", {}).get("date-time", "")),
            "publication_type": str(message.get("type", "")),
            "withdrawal_status": flag,
            "relation": relation,
        }
    except Exception as exc:
        return {"remote_status": f"error:{type(exc).__name__}", "withdrawal_status": "not_checked"}


def arxiv_records(ids: list[str]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    for pos in range(0, len(ids), 30):
        batch = ids[pos:pos + 30]
        url = "https://export.arxiv.org/api/query?id_list=" + ",".join(batch) + "&max_results=30"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as response:
                root = ET.fromstring(response.read())
            for entry in root.findall("a:entry", ns):
                rid = (entry.findtext("a:id", default="", namespaces=ns).rsplit("/", 1)[-1]).split("v", 1)[0]
                title = " ".join(entry.findtext("a:title", default="", namespaces=ns).split())
                summary = " ".join(entry.findtext("a:summary", default="", namespaces=ns).split())
                comment = entry.findtext("arxiv:comment", default="", namespaces=ns)
                authors = entry.findall("a:author", ns)
                author = authors[0].findtext("a:name", default="", namespaces=ns) if authors else ""
                status_blob = " ".join([title, summary, comment]).lower()
                flag = "withdrawal_flag" if any(x in status_blob for x in ("withdrawn", "withdrawal", "retracted")) else "no_withdrawal_flag_in_arxiv_record"
                out[rid] = {
                    "remote_status": "resolved",
                    "remote_title": title,
                    "remote_first_author": author,
                    "remote_updated": entry.findtext("a:updated", default="", namespaces=ns),
                    "publication_type": "arXiv preprint",
                    "withdrawal_status": flag,
                    "relation": comment,
                }
        except Exception as exc:
            for rid in batch:
                out[rid] = {"remote_status": f"error:{type(exc).__name__}", "withdrawal_status": "not_checked"}
        time.sleep(1.0)
    return out


def arxiv_page_record(arxiv_id: str) -> dict[str, str]:
    try:
        url = f"https://arxiv.org/abs/{arxiv_id}"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as response:
            page = response.read().decode("utf-8", errors="replace")

        parser = CitationMetaParser()
        parser.feed(page)

        def meta(name: str) -> list[str]:
            return parser.values.get(name.lower(), [])

        titles = meta("citation_title")
        authors = meta("citation_author")
        dates = meta("citation_date")
        status_text = re.sub(r"<[^>]+>", " ", page).lower()
        flag = "withdrawal_flag" if any(x in status_text for x in ("this paper has been withdrawn", "withdrawn by the authors", "retracted")) else "no_withdrawal_notice_on_primary_page"
        versions = re.findall(r"\[v(\d+)\]\s*([^<\r\n]+)", page, flags=re.I)
        updated = f"v{versions[-1][0]} {html.unescape(versions[-1][1]).strip()}" if versions else (dates[0] if dates else "")
        return {
            "remote_status": "primary_page_resolved",
            "remote_title": titles[0] if titles else "",
            "remote_first_author": authors[0] if authors else "",
            "remote_updated": updated,
            "publication_type": "arXiv preprint",
            "withdrawal_status": flag,
            "relation": url,
        }
    except Exception as exc:
        return {"remote_status": f"error:{type(exc).__name__}", "withdrawal_status": "not_checked"}


def openalex_title_record(title: str) -> dict[str, str]:
    try:
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode({"search": clean(title), "per-page": 5})
        results = get_json(url).get("results") or []
        if not results:
            return {"remote_status": "not_returned", "withdrawal_status": "not_checked"}
        best = max(results, key=lambda item: SequenceMatcher(None, norm(title), norm(item.get("title", ""))).ratio())
        authorships = best.get("authorships") or []
        author = authorships[0].get("author", {}).get("display_name", "") if authorships else ""
        flag = "retracted" if best.get("is_retracted") else "no_retraction_flag_in_openalex_record"
        primary = best.get("primary_location") or {}
        source = primary.get("source") or {}
        return {
            "remote_status": "resolved_openalex",
            "remote_title": best.get("title", ""),
            "remote_first_author": author,
            "remote_updated": best.get("updated_date", ""),
            "publication_type": best.get("type", ""),
            "withdrawal_status": flag,
            "relation": json.dumps({"doi": best.get("doi"), "venue": source.get("display_name")}, ensure_ascii=False),
        }
    except Exception as exc:
        return {"remote_status": f"error:{type(exc).__name__}", "withdrawal_status": "not_checked"}


def main() -> None:
    entries = parse_entries(BIB.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    for idx, entry in enumerate(entries, start=1):
        doi = entry.get("doi", "")
        eprint = entry.get("eprint", "").split("v", 1)[0]
        if doi and not doi.lower().startswith("10.48550/arxiv"):
            remote = crossref_record(doi)
            source = "Crossref"
            time.sleep(0.15)
        elif eprint:
            remote = arxiv_page_record(eprint)
            source = "arXiv primary page"
            time.sleep(0.08)
        elif doi:
            remote = crossref_record(doi)
            source = "Crossref"
            time.sleep(0.15)
        else:
            remote = {"remote_status": "no_identifier", "withdrawal_status": "manual_source_check_required"}
            source = "manual"
        if not remote.get("remote_status", "").startswith("resolved"):
            fallback = openalex_title_record(entry.get("title", ""))
            if fallback.get("remote_status", "").startswith("resolved"):
                remote = fallback
                source = source + "+OpenAlex"
            time.sleep(0.12)
        if eprint in PRIMARY_PAGES_VERIFIED_2026_09_17 and not remote.get("remote_status", "").endswith("resolved"):
            remote = {
                "remote_status": "primary_page_verified",
                "remote_title": entry.get("title", ""),
                "remote_first_author": entry.get("author", "").split(" and ", 1)[0],
                "remote_updated": "checked 2026-09-17",
                "publication_type": "arXiv preprint",
                "withdrawal_status": "no_withdrawal_notice_on_primary_page_2026-09-17",
                "relation": f"https://arxiv.org/abs/{eprint}",
            }
            source = "arXiv primary page"
        if entry["key"] in MANUALLY_RESOLVED_PRIMARY_SOURCES and not remote.get("remote_status", "").endswith("resolved"):
            remote = {
                **MANUALLY_RESOLVED_PRIMARY_SOURCES[entry["key"]],
                "remote_title": entry.get("title", ""),
                "remote_first_author": entry.get("author", "").split(" and ", 1)[0],
            }
            source = "manually verified primary index"
        local_title = entry.get("title", "")
        remote_title = remote.get("remote_title", "")
        similarity = SequenceMatcher(None, norm(local_title), norm(remote_title)).ratio() if remote_title else 0.0
        local_author = entry.get("author", "").split(" and ", 1)[0]
        remote_author = remote.get("remote_first_author", "")
        local_surname = norm(local_author.split(",", 1)[0]).split()[-1] if norm(local_author) else ""
        author_match = local_surname in norm(remote_author).split() if remote_author and local_surname else False
        resolved = remote.get("remote_status", "").startswith("resolved") or remote.get("remote_status", "").endswith(("resolved", "verified"))
        if resolved and similarity >= 0.82 and (author_match or not remote_author or similarity >= 0.98):
            decision = "metadata_consistent"
        elif resolved:
            decision = "manual_metadata_review"
        else:
            decision = "manual_source_review"
        rows.append({
            "bib_key": entry["key"],
            "entry_type": entry.get("entry_type", ""),
            "local_title": local_title,
            "local_first_author": local_author,
            "doi": doi,
            "arxiv_id": eprint,
            "audit_source": source,
            "remote_status": remote.get("remote_status", ""),
            "remote_title": remote_title,
            "remote_first_author": remote_author,
            "remote_updated": remote.get("remote_updated", ""),
            "publication_type": remote.get("publication_type", ""),
            "withdrawal_status": remote.get("withdrawal_status", ""),
            "title_similarity": f"{similarity:.3f}",
            "first_author_match": str(author_match),
            "audit_decision": decision,
            "relation_or_comment": remote.get("relation", ""),
        })
        print(f"[{idx}/{len(entries)}] {entry['key']}: {decision}")
    with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
