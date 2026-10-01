# Experiment Extraction Rules

This file defines how experiment cells are separated and linked in `experiment_registry.csv` and `claim_experiment_links.csv`. Approved pilot records are retained unchanged as an audit trail.

1. Within one source, create separate experiment cells when the platform or setting, policy or model, task suite, action space, experimental direction, cohort, or native denominator differs.
2. Do not create separate cells merely because the reported metric or baseline differs when the same data and protocol are used.
3. For method-definition claims, leave `Experiment_ID` blank and use `Not_Applicable_Method`.
4. When a source reports an experiment without a corresponding atomic claim, set `Claim_Coverage_Status` to `Claim_Gap_Identified`, retain the source's actual verification status, and do not create a claim--experiment link.
5. When the denominator or setting cannot be confirmed from the source, retain cautious source wording and set `Verification_Status` to `Needs_Source_Check`.
6. Do not substitute participant, task, or scenario counts for unreported event or episode denominators.
7. One claim may link to several experiment cells, and one experiment cell may support several claims.
8. `Study_ID` uses the four digits of the study's earliest `Claim_ID`; `Experiment_ID` uses `Study_ID-E##`. Once assigned, identifiers are not reordered or reused after additions or deletions.
9. Permitted `Verification_Status` values are `Pilot_Checked`, `Draft_Unchecked`, `Source_Checked`, and `Needs_Source_Check`. Use `Draft_Unchecked` only for records awaiting review; use `Needs_Source_Check` only when a specific ambiguity remains in the source itself.
10. `Claim_Coverage_Status` records claim coverage, not source verification. Permitted values are `Not_Assessed`, `Linked`, and `Claim_Gap_Identified`.
