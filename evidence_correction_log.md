# Evidence correction log

## 2026-09-16: source-audit batch 1

This log records source-level corrections made after the structural experiment-migration audit. A structural PASS establishes registry integrity; it does not by itself establish that every denominator, numerical result, evaluation setting, or source locator is scientifically correct.

| Claim | Correction | Source basis | Downstream effect |
|---|---|---|---|
| CL-0088 | LIBERO Table 2 denominator changed from 1,000 pooled OpenVLA/pi0-FAST rollouts to 500 pi0-FAST rollouts. The separate 500-rollout OpenVLA cohort belongs to Table 4 transfer evaluation. | Foresight, Sec. 5.4, Table 2, Appendix 11.1, Tables 7-8 | Prevents cross-protocol denominator pooling. |
| CL-0158 | RoboSafe immediate-unsafe mean ARR changed from 89.22% to 89.89%. | RoboSafe, Table 1: mean of 92.33%, 87.33%, and 90.00% | Corrects the claim-level aggregate. |
| CL-0189 | Setting changed from closed-loop simulation to offline digital evaluation; locator and transfer boundary clarified. | SafeMind, Secs. 3.1-3.2, 4.3, 6.2.2, Table 3, Appendix A.2 | Prevents symbolic action-sequence judging from being counted as closed-loop execution. |
| CL-0224 | Setting changed from closed-loop simulation to offline digital evaluation; pooled GRU AUC span corrected from 0.975-0.982 to 0.973-0.982. | Tri-Info, Secs. 4-5.3 and Table 1 | Prevents post-hoc logged-trajectory analysis from being counted as a connected runtime monitor. |
| CL-0225 | Setting changed from controlled real robot to offline digital evaluation of physical-rollout logs; terminal balanced accuracy recorded as the source-reported 0.83; denominator fixed at 26 success + 34 failure = 60. | Tri-Info, Sec. 5.2, Figure 5, Appendix C.1, Table 8 | Retains physical data provenance without overstating runtime execution. |
| CL-0250 | Setting changed from controlled real robot to closed-loop simulation; scope tied to the SafeLIBERO discussion and physical-frequency inference prohibited. | VLSA, Sec. V-C, immediately following SafeLIBERO results | Prevents simulation-associated limitations from being counted as quantified physical evidence. |

Experiment-status changes in this batch:

- ST-0086-E01 to E03: `Pilot_Checked` to `Source_Checked`.
- ST-0186-E050: `Needs_Source_Check` to `Source_Checked`; the unresolved exact post-extraction category denominator is retained as a source limitation.
- ST-0245-E01 to E02: `Needs_Source_Check` to `Source_Checked`; 1,600 is retained as the benchmark evaluation-pass denominator, while the paper's unstated aggregate execution total across configurations remains explicit.

Registry totals after this batch: 1,912 `Source_Checked`, 15 `Pilot_Checked`, and 213 `Needs_Source_Check`, totaling 2,140 experiment records.

## 2026-09-17: source-audit batch 2

This batch audited the complete linked FailSafe experiment block against arXiv:2510.01642v4, with particular attention to observation viewpoint, runtime authority, simulator execution, and denominator granularity.

| Claim | Correction or confirmation | Source basis | Downstream effect |
|---|---|---|---|
| CL-0082 | Replaced “multi-view execution window” with a ten-frame runtime window from the camera view shared with the base VLA. The three-view description belongs to dataset construction. The setting is now `Mixed_Settings` because the claim combines runtime simulator integration with a separate 1,712-entry offline evaluation. | Sec. III-D; Fig. 3; Secs. IV-A and IV-C; Table V | Prevents dataset-view design from being misreported as the runtime monitor interface and prevents offline component metrics from being counted wholly as closed-loop evidence. |
| CL-0083 | Confirmed that FailSafe-VLM temporarily takes control in ManiSkill, issues a directly executable 7-DoF corrective action, and returns control to the base VLA. Placement is recorded as an external monitor/controller. | Sec. IV-A; Fig. 3; Table II; Sec. V | Preserves intervention authority while retaining the prohibition on inferring independently verified safe-state recovery. |
| CL-0084 | Confirmed every Table II success value. Added the Table VI statement that each VLA comparison is averaged across 75 runs, while retaining `NR` for the unreported per-task and per-condition allocation. | Tables II and VI; Secs. IV-A and IV-D | Makes the reported denominator boundary explicit without inferring 25 trials per cell from percentage increments. |

Experiment-status changes in this batch:

- ST-0082-E04 to ST-0082-E12: `Needs_Source_Check` to `Source_Checked`; Table II values and the 75-run VLA-level aggregate were confirmed, while per-task/per-condition allocation remains not reported.
- ST-0082-E13 to ST-0082-E15: `Needs_Source_Check` to `Source_Checked`; Table III values were confirmed and the unreported evaluation denominator remains explicit.
- ST-0082-E16 to ST-0082-E18: `Needs_Source_Check` to `Source_Checked`; Table IV values were confirmed, and the 1,000 trajectories per task are retained as fine-tuning data rather than misused as evaluation denominators.

Registry totals after this batch: 1,927 `Source_Checked`, 15 `Pilot_Checked`, and 198 `Needs_Source_Check`, totaling 2,140 experiment records.

## 2026-09-17: source-audit batch 3

This batch audited the complete ST-0151 maritime supervisory-control block against the published Journal of Marine Science and Technology article (DOI 10.1007/s00773-023-00945-6).

| Claim | Correction or confirmation | Source basis | Downstream effect |
|---|---|---|---|
| CL-0151 | Replaced the placeholder locator with the STPA sections, Tables 1–11, and system diagrams. Removed a duplicated transfer phrase. | Secs. 2.2 and 3.1–3.4; Tables 1–11; Figs. 1–2 | Restores traceability for the qualitative hazard, safety-constraint, unsafe-control-action, and loss-scenario claim. |
| CL-0152 | Added the exact slack-variable, safety-inequality, exponential-risk-cost, and RPN locations. Cleared an inapplicable intervention-authority value because this claim concerns signal construction. | Secs. 4.1–4.4; Eqs. (1)–(3); Table 12 | Preserves the risk cost as a model-based optimization signal rather than a calibrated collision probability or an intervention event. |
| CL-0153 | Added the nonlinear OCP/NLP and receding-horizon controller locations. | Secs. 5.1–5.4; Eqs. (4)–(16); Sec. 6.1 | Bounds machine authority to modeled route/control decisions in the simulated planner. |
| CL-0154 | Verified all nine displayed conditions in Figures 3–11 and recorded the source's visual/human-assessment verification method. | Sec. 6.1; Figs. 3–11; Sec. 7.3 | Retains scenario-specific trajectory evidence without manufacturing collision-prevention rates or independent-run denominators. |
| CL-0155 | Corrected the timing description from a single maximum-only sequence to nine displayed sequences taking 6.5–12.4 s, each containing 20 optimizations of 40 future intervals. Cleared an inapplicable intervention-authority value. | Sec. 6.1, paragraph after Fig. 11; Secs. 7.6 and 8.3–8.5 | Preserves component/setup timing while excluding sensing, communication, actuation, solver-failure handling, and field deadline guarantees. |

Experiment-status changes in this batch:

- ST-0151-E01 to ST-0151-E09: `Needs_Source_Check` to `Source_Checked`; every Figure 3–11 scenario description was checked, while collision counts, independent repeats, and condition-specific timing remain explicitly unreported.
- ST-0151-E10 was already `Source_Checked`; its pooled timing interpretation was rechecked with the source-level performance paragraph.

Bibliographic correction: `Blindheim2023ShipSupervisory` was changed from `@misc` to its published journal form with journal, volume, pages, and DOI. The study is now cited in the runtime-monitoring discussion as Adjacent planner-interface evidence.

Registry totals after this batch: 1,936 `Source_Checked`, 15 `Pilot_Checked`, and 189 `Needs_Source_Check`, totaling 2,140 experiment records.

## 2026-09-17: source-audit batch 4

This batch audited all 75 ST-0241 VLA-FAIL experiment cells against arXiv:2606.21386v1, with particular attention to the 24 previously unresolved LIBERO-Plus cells and to the distinction between detector scoring and executed safety intervention.

| Claim | Correction or confirmation | Source basis | Downstream effect |
|---|---|---|---|
| CL-0241--CL-0242 | Confirmed LLMD and ACC as runtime-computable monitor signals, while retaining the boundary that neither is connected to action authority or a recovery mechanism in the reported evaluation. | Secs. 3.1--3.3; Eqs. (1)--(7); Sec. 6 | Prevents a detector score from being promoted to an executed safety response. |
| CL-0243 | Replaced the incorrect “roughly 80 rollouts total” description with the exact calibration, ID, and OOD rollout counts for every real-robot model--task cell. The evidence locator now includes Tables 12--13 and Appendix F. | Table 1; Appendix F.1--F.2; Tables 12--13 | Makes the physical-trajectory denominator auditable while retaining `NR` for exact failed-episode counts. |
| CL-0244 | Corrected the fourth LIBERO-Plus suite label from “Long” to “10”; added the suite-level calibration and rollout counts from Table 14; and retained the source-level ambiguity over whether each rollout count is per backbone or shared/pooled. | Table 2; Appendix F.1 and F.3; Table 14 | Supports quantitative simulation evidence without manufacturing a per-backbone denominator or merging simulation with physical results. |

Experiment-status changes in this batch:

- ST-0241-E25 to ST-0241-E40: `Needs_Source_Check` to `Source_Checked`; threshold-independent and fixed-threshold LIBERO-Plus result cells, single-seed protocol, suite-level calibration counts, and rollout-count ambiguity were checked.
- ST-0241-E63 to ST-0241-E70: `Needs_Source_Check` to `Source_Checked`; the velocity-normalization ablations and their Table 14 denominator boundary were checked.
- ST-0241-E01 to ST-0241-E24 and ST-0241-E41 to ST-0241-E62, E71 to E75 were already `Source_Checked`; their physical-rollout, ablation, overlap-sweep, and latency interpretations were rechecked against the same source.

Registry totals after this batch: 1,960 `Source_Checked`, 15 `Pilot_Checked`, and 165 `Needs_Source_Check`, totaling 2,140 experiment records.

## 2026-09-17: source-audit batch 5

This batch closed all 91 experiment cells that were linked to a coded claim but had not yet received full source-level verification. To avoid leaving partially audited studies, 47 additional claim-gap cells from the same source blocks were also checked, for 138 status closures in total.

| Claim or study block | Correction or confirmation | Source basis | Downstream effect |
|---|---|---|---|
| CL-0057 / CoFreeVLA | Recorded an internal source conflict: Figure 2 and the prose in Sections 4.1--4.2 disagree on baseline collision/task-success counts. Figure-specific method values are retained, but comparative effect claims are blocked. | Figure 2; Sections 4.1--4.2 | Prevents an internally inconsistent physical comparison from entering synthesis as a resolved effect estimate. |
| CL-0106 / LabRobFail | Recorded that the OpenVLA Pick row prints `19/25` together with `84\%`, although 19/25 equals 76\%. The printed pair is preserved as a source inconsistency rather than silently corrected. | Tables 2--4 | Prevents an untraceable arithmetic repair and keeps the numerator/percentage conflict visible. |
| CL-0130 / Pre-VLA | Reclassified 10,000 episodes as a suite-level budget spanning the compared methods; per-method allocation remains not reported. | Evaluation protocol and result tables | Prevents the suite budget from being multiplied or assigned to each method without evidence. |
| CL-0200 / takeover schedule | Replaced the claim that 252 events were verified TORs with 252 planned condition exposures. The paper says nine TORs per participant but also states that manual-driving cells required no takeover, so the exact TOR denominator is unresolved. | Sections II-C--D and III; Figures 3 and 5--11 | Prevents manual baseline trials from being counted as automation-to-manual acquisition events. |
| Foresight, RC-NF, VLSA timing | Confirmed 183 ms per Foresight replan, 86.7 ms for the RC-NF detector pipeline, and 0.355--0.357 ms for the VLSA safety layer. None is treated as full signal-to-actuation latency. | Foresight Table 14; RC-NF Supplement Sec. 5; VLSA Figure 10 | Preserves component-level timing without manufacturing end-to-end deadline evidence. |
| SAFE, Temporal Calibration, human-transition studies | Confirmed the reported model/task metrics while retaining unresolved per-model/per-seed or event-level denominators. | SAFE Tables 1, 5, 8; Temporal Calibration Figures 4--5; transition-study Table 2 | Supports bounded quantitative synthesis while keeping denominator uncertainty explicit. |

Experiment-status changes in this batch:

- 79 linked `Needs_Source_Check` cells and 12 linked `Pilot_Checked` cells were changed to `Source_Checked` after source-level verification.
- 47 additional `Needs_Source_Check` claim-gap cells in the same fully audited study blocks were changed to `Source_Checked`.
- All 891 claim-linked experiment cells are now `Source_Checked`; no linked cell remains at pilot or pending-source status.
- The remaining 42 non-source-checked cells (39 `Needs_Source_Check`, 3 `Pilot_Checked`) are all `Claim_Gap_Identified` and do not support any current coded claim.

Registry totals after this batch: 2,098 `Source_Checked`, 3 `Pilot_Checked`, and 39 `Needs_Source_Check`, totaling 2,140 experiment records.

## 2026-09-17: source-audit batch 6

This batch audited the final 42 non-source-checked experiment cells against the 14 corresponding full-text sources. All 42 are `Claim_Gap_Identified`; none supports a current coded claim, and none changes the 891 claim-linked experiment-cell statistics.

| Study block | Correction or confirmation | Source basis | Downstream effect |
|---|---|---|---|
| Act/Think/Abstain; adversarial VLA attack; SAFE-Dict | Confirmed the data-scaling fractions, the HYDRA/SIMPLER ASR columns, and the Qwen2.5-VL transfer reference. The 100% scaling-point count and HYDRA denominator remain unreported. Table 2 of the attack paper repeats ``SIMPLER'' in its caption, whereas Section 4.1 and the column header identify HYDRA as the real-image environment; this source typo is now explicit in the registry. | Act/Think/Abstain Fig. 4 and Sec. IV-A; adversarial VLA attack Sec. 4.1, Table 2, Appendix A; SAFE-Dict Table 4 | Preserves the reported results without assigning the SIMPLER 120-target denominator to HYDRA or inferring an unstated full-data count. |
| EMBGuard; Foresight; runtime governance | Confirmed both inference-time values, dataset-overlap percentages, scene-composition table, real-robot and cross-policy Foresight blocks, and all six violation-type detection rates. Unreported timing repetitions and realized per-violation counts remain `NR`. | EMBGuard Sec. 4.2 and Appendix Tables 7--9; Foresight Tables 3--4 and Appendix Tables 8 and 11; runtime-governance Secs. 4.1--4.7 and Table 6 | Keeps component timing separate from end-to-end latency and avoids deriving type-level denominators from nominal uniform sampling. |
| SafeContract; Lost in Fog; PaCo-VLA | Confirmed conformal coverage/tightness, monitoring overhead, all four preprocessing-defense result rows, and both direct-action comparison groups. Group-level sample sizes are retained without assigning them independently to every comparator row. | SafeContract Secs. II and IV; Lost in Fog Sec. 4.3 and Table 9; PaCo-VLA Sec. 5.4, Table 3, Appendix B.2--B.4 | Preserves calibration, component-timing, and group-level evaluation boundaries. |
| SABER; reach-avoid RL | Confirmed the pooled GPT-5-mini comparison, cold-start ablation, and two-round exhaustive policy-validation protocol. Victim/cohort attribution in SABER and whether 500 reach-avoid states applies per value-sign group or in total remain unresolved by the sources. | SABER Sec. V-D and Tables V--VI; reach-avoid RL Sec. IV-D and Fig. 7 | Prevents contextual inferences from becoming fabricated denominators. |
| Tex3D; diversity-aware red teaming; VISTA | Visually checked Tex3D Figures 4, 6, and 7; confirmed all robustness-curve values, defense-strength labels, two LPIPS pairs, and six displayed SSIM comparisons. Confirmed the 270-episode CALVIN statement and all four VISTA component-ablation values. Seed allocation and ablation-cohort reuse remain source-level limitations. | Tex3D Sec. 4.3 and Figs. 4, 6--7; diversity-aware red teaming Sec. 5.5 and Fig. 2(a); VISTA Sec. 4.4, Table 8, and Appendix D | Corrects the displayed SSIM comparison count while retaining `NR` for the broader sampling protocol and other unstated allocations. |

Experiment-status changes in this batch:

- 39 `Needs_Source_Check` claim-gap cells were changed to `Source_Checked`.
- Three `Pilot_Checked` Foresight claim-gap cells were changed to `Source_Checked`.
- The registry now contains no `Needs_Source_Check`, `Pilot_Checked`, or temporary verification states.

Registry totals after this batch: 2,140 `Source_Checked`, 0 `Pilot_Checked`, and 0 `Needs_Source_Check`, totaling 2,140 experiment records.
