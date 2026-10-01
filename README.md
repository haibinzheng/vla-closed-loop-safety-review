# Closed-loop VLA safety review: data and reproduction scripts

This repository provides the supporting review tables and reproduction scripts for *Closed-Loop Safety and Runtime Assurance for Vision-Language-Action Systems: A Critical Evidence Review*. It does not contain model weights, robot training data, or copies of the reviewed papers.

## Quick start

Use Python 3.10 or newer. The supplied scripts use the Python standard library; no third-party packages are required for the offline checks below. Download the repository, open a terminal in its root directory, and run:

```text
python reconstruct_frozen_evidence_chain_statistics.py --check
python summarize_late_update_sensitivity.py
python build_priority_sensitivity_sample.py
```

The first command checks the reconstructed frozen evidence-chain counts against the released statistics. The other commands reproduce the separate late-update summary and priority sensitivity sample. Run the live search and bibliography audit scripts only when an updated retrieval is intended: live services may return different results from the archived search.

## Release scope

The repository contains the compact supporting package. Large raw service-response files, copyrighted source PDFs, manuscript drafts, credentials, and local build files are not included. The supporting tables are not a complete record-level archive of every candidate in the historical 979-record search queue; the scope and denominators of the supplied records are described below. Relative PDF paths in crosswalks are provenance identifiers, not downloadable source files.

The associated manuscript is a research manuscript; this repository does not imply journal acceptance or publication. No DOI or journal publication details have been assigned here.

This package accompanies *Closed-Loop Safety and Runtime Assurance for Vision-Language-Action Systems: A Critical Evidence Review*. It contains the review records and scripts needed to audit the reported search, screening, claim, experiment, and evidence-chain counts. Copyrighted article PDFs are not redistributed.

## Final search update

- `final_search_log.csv`: database, query family, exact query, execution time, date bounds, status, and returned-row count for all 15 search operations.
- `final_search_records.csv`: normalized and identifier/title-keyed records returned by arXiv, OpenAlex, and Crossref.
- `final_search_summary.json`: aggregate final-search counts.
- `final_update_screen.csv`: record-level priority, retrieval, eligibility, and final-disposition decisions.
- `final_update_screen_summary.json`: final-update disposition counts.
- `final_update_qualitative_synthesis.csv`: structured findings for the 41 eligible late-update studies used in the separate study-level sensitivity check.
- `late_update_structured_counts.csv`: study-level relation, node, and node-co-occurrence counts reconstructed from the existing mapping; it is not claim-level recoding and is not pooled with frozen quantitative denominators.
- `final_update_priority_sensitivity_sample.csv`: reproducible 30-record sample from the residual non-priority exact-VLA pool (random seed 62406286); no sampled record required promotion after the complete routing repair.
- `bibliography_2026_status_audit.csv`: status, title, author, version-date, publication-type, and withdrawal/retraction checks for all 92 bibliography entries dated 2026.

The final update covered 29 July--17 September 2026. It comprised 15 source-by-query-family operations. The services reported 14,883 results, 9,744 source rows were retrieved, and normalization plus identity reconciliation yielded 4,394 identifier/title-keyed records. An exact-VLA metadata filter yielded 386 unique titles. The mutually exclusive routing procedure assigned 64 records to the priority stratum and 322 to the residual non-priority stratum. Within the priority stratum, 14 were excluded at metadata screening, two matched existing studies, and 48 proceeded to retrieval. Forty-five full texts or authoritative full-text records were obtained and three remained source-deferred; 41 studies were retained and four were excluded after full-text review. The 41 studies form a separate structured study-level sensitivity set and were not added retrospectively to the frozen quantitative denominators.

## Frozen quantitative evidence base

- `status_closed_claims.csv`: 254 source-closed atomic claims.
- `frozen_corpus_dispositions.csv`: one row for each of the 78 obtained pre-update full texts, with its final disposition and claim count.
- `traceability_study_registry.csv`: 248-study identity/provenance inventory. It is not the screening denominator and contains no pending coordinator workflow fields.
- `f4r1_claim_study_crosswalk.csv`: claim-to-study crosswalk.
- `h0_pdf_study_crosswalk.csv`: source-file-to-study crosswalk.
- `experiment_registry.csv`: 2,140 source-checked experiment cells.
- `claim_experiment_links.csv`: claim-to-experiment links.
- `evidence_chain_statistics.csv`: statistics used for the evidence-chain figure and quantitative synthesis.
- `evidence_correction_log.md`: material source corrections and audit trail.
- `experiment_extraction_rules.md`: extraction and unit-definition rules.
- `references.bib`: bibliography version used by the 2026 status audit.

## Reproduction scripts

- `final_search_update.py`: executes and normalizes the final API search.
- `build_final_update_screen.py`: applies the declared priority rules.
- `build_priority_sensitivity_sample.py`: reconstructs the mutually exclusive priority/residual partition and draws the seeded residual sensitivity sample.
- `repair_final_update_routing.py`: merges the complete route with the audited final dispositions while preserving the frozen claim corpus.
- `finalize_final_update_screen.py`: records final full-text dispositions and generates the qualitative synthesis.
- `audit_2026_bibliography.py`: resolves 2026 DOI and arXiv records and flags metadata or withdrawal/retraction discrepancies.
- `summarize_late_update_sensitivity.py`: reconstructs the separate study-level sensitivity counts without altering the frozen claim corpus.
- `reconstruct_frozen_evidence_chain_statistics.py`: rebuilds all 37 rows of `evidence_chain_statistics.csv` from the released claim and claim--experiment tables and can verify an exact match with `--check`.

All scripts detect whether they are running in the project tree or directly inside this submission directory. In package mode, `build_final_update_screen.py` writes `reconstructed_preliminary_screen.csv` so that it cannot overwrite the audited final decisions. `finalize_final_update_screen.py` rebuilds the qualitative synthesis and summary from the supplied, author-verified `final_update_screen.csv`; copyrighted PDFs are not required. The live search and bibliography audit require network access, whereas the screen, sample, disposition, and count reconstructions use only supplied files.

The PDF acquisition and text-extraction helpers are retained in the project repository but are not required to recompute manuscript counts and are therefore not included in the compact submission archive.

## Interpretation boundaries

The pre-update accounting is 979 title-level candidates, 203 acquisition priorities, 78 obtained full texts, 73 coding candidates, 56 coded studies, and 254 claims. The frozen quantitative synthesis comprises 56 studies, 254 claims, and a registry of 2,140 experiment cells. Of those cells, 891 are claim-linked and define the cell-level denominator used in Figure 8; 1,249 additional source-reported cells do not support a separate atomic claim. The 41-study final-update set is a separate structured study-level sensitivity check, not claim-level recoding, and is not pooled with those denominators. Counts should be regenerated only from the named frozen files and with the unit definitions preserved.
