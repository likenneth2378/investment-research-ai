# Failure Cases

This document records failures that materially changed the product design.

The goal is not to catalogue ordinary coding mistakes. The useful failures here are cases where an LLM or workflow could produce a plausible-looking output that is misleading, expensive to review, or difficult to audit.

All public examples below are syntheticized or taken from the synthetic demo. Confidential research materials are not reproduced.

---

## 1. Attribution stripping

**Observed failure**

Source:

> 公司称目前涉及 11 项核心专利。

Bad model compression:

> 公司拥有 11 项核心专利。

**Why it matters**

The model removed who made the statement. In investment research, a company-reported statement and an independently verified fact are not equivalent.

**Design response**

- preserve `source_text`;
- preserve `attribution`;
- prevent company-reported language from silently becoming objective fact;
- require final summary statements to retain a link back to evidence.

**Current status**

Mitigated in the current workflow, but retained as a regression case.

---

## 2. Historical fact misclassified as projection

**Observed failure**

Source:

> 2025 年实现营收 1.26 亿元。

Incorrect classification:

`Projection`

A genuinely forward-looking statement would look like:

> 2026 年预计营收达到 3 亿元。

**Why it matters**

Historical performance and forward guidance have different meanings in investment analysis.

**Design response**

Projection status is now treated as a semantic property that must survive extraction and final-summary verification rather than as a stylistic label.

**Current status**

Retained as a regression case. A larger labeled benchmark is still needed.

---

## 3. Measurable claim mistaken for “marketing”

**Observed failure**

Source:

> 公司称其系统可使项目综合收益提升约 15%。

The claim was classified as `Projection` in one test and `Subjective / Marketing` in another.

**Why it matters**

The statement may be promotional, but it is also measurable. The research problem is whether the 15% improvement is supported, not whether the sentence sounds promotional.

**Design response**

Working distinction:

- measurable but not independently supported → `Unverified`
- explicitly forward-looking → `Projection`
- non-measurable positioning language → `Subjective / Marketing`

---

## 4. Timeline progression mistaken for contradiction

**Synthetic example**

Material A:

> 截至 2026 年 3 月，公司累计完成 27 个项目。

Material B:

> 截至 2026 年 6 月，公司累计完成 30 个项目。

A naive contradiction detector may flag 27 vs. 30.

**Why it matters**

The two values can both be correct if they refer to different dates.

**Design response**

Same topic is not enough to create a conflict. The workflow now distinguishes:

- timeline progression;
- complementary information;
- version revision;
- scope difference;
- potential conflict.

Only review-worthy cases should be promoted into Research Flags.

---

## 5. Application scenario inflated into business traction

**Observed failure pattern**

Source meaning:

> 某技术可以用于金融风险控制和投资组合优化。

Overstated output:

> 公司开展金融领域业务。

**Why it matters**

A potential use case is not evidence of a customer, deployment, contract, revenue stream or operating business.

**Design response**

The current fact schema distinguishes:

- `application_scenario`
- `customer_reference`
- `order_signed`
- `purchase_intent`
- revenue / financing / valuation facts

User-facing summaries are instructed to use “应用场景 / 方案 / 潜在用途” unless there is actual business-traction evidence.

**Current status**

Added to the current extraction and synthesis rules and retained as a regression target.

---

## 6. Over-extraction: traceability without time saving

**Observed failure**

An early real-document test produced a very large number of individual facts. The output was traceable, but reading the result felt close to reading the original document again.

**Why it matters**

A research tool can be technically auditable and still fail its main product goal if it does not reduce analyst reading time.

**Design response**

The interface moved away from a Claim Ledger as the primary view.

Current hierarchy:

```text
Snapshot
→ Research Matrix
→ Flags
→ Sources / Evidence on demand
```

The underlying facts remain available as an evidence substrate, but they are not the default reading interface.

---

## 7. Evidence UI became a second copy of the document

**Observed failure**

Early evidence cards displayed source text, nearby context, visual extraction and page previews by default.

**Why it matters**

The evidence layer added review work instead of reducing it.

**Design response**

Evidence is now collapsed by default. The user sees a compact source reference first and expands evidence only when needed.

---

## 8. Vision overuse increased cost and latency

**Observed failure**

A previous heuristic called vision analysis on too many pages because image count and page layout were treated as enough reason to inspect a page visually.

**Why it matters**

Vision was often the dominant source of latency and cost even when the PDF text layer already contained the useful information.

**Design response**

- text-first parsing;
- page triage before visual analysis;
- visual analysis only when an important page is text-insufficient;
- hard cap on visual units per run.

---

## 9. Structured-output formatting broke otherwise useful extraction

**Observed failure**

Models returned variations such as:

```text
[UNIT Page 14]
UNIT Page 14
Page 14
```

A strict validator originally accepted only the last format and discarded otherwise usable facts.

Other observed structured-output failures included code fences, malformed JSON, truncated strings and missing fields.

**Why it matters**

A workflow should not lose good semantic output because of harmless formatting variation.

**Design response**

- canonical source-location normalization;
- schema validation;
- tolerant parsing where safe;
- item-level rejection instead of failing an entire batch;
- lightweight smoke tests before running a full document.

---

## 10. Verification became the latency bottleneck

**Observed behavior**

Stage timing showed that final semantic verification could take longer than triage, extraction or synthesis.

The original verifier reread the facts and regenerated the complete research output.

**Why it matters**

A reliability layer that doubles the generation work can make the product too slow and expensive.

**Design response**

The verifier now performs an **issue-only audit**:

```text
research output
→ verifier checks each item
→ returns only problematic targets
→ Python applies replace / drop operations
```

Correct items do not need to be regenerated.

**Current status**

Implemented; latency reduction still needs repeated benchmarking.

---

## 11. Material caveat lost during synthesis

**Observed failure**

The structured facts were individually correct:

> 公司称目前涉及 11 项核心专利，其中 5 项为合作开发。

> 其中 3 项仍处于申请或开发阶段，尚未形成已授权专利。

But the Research Matrix compressed the topic to only:

> 公司称目前涉及 11 项核心专利，其中 5 项为合作开发。

**Why it matters**

The remaining sentence is technically supported, but it changes how a reader interprets the 11-patent headline by hiding a decision-relevant qualifier. Faithful compression is not only about avoiding invented facts; it must also preserve caveats that materially change the meaning of a claim.

**Design response**

- synthesis must preserve material qualifiers from related facts;
- grouped summaries must reference all facts that materially qualify the headline claim;
- the issue-only verifier now checks for dropped qualifiers such as cooperation status, authorization status, purchase intent vs. signed order, and planned vs. realized capacity.

**Current status**

Added as a Demo regression target and verifier rule.

---

## 12. Superseded forecast shown as the current state

**Observed failure**

The evidence contained both:

> 管理层预计 2026 年全年营收达到 3 亿元。

and a later explicit revision:

> 管理层将 2026 年全年营收目标调整为 3.2 亿元。

The Matrix still displayed the older 3 亿元 figure as the current summary.

**Why it matters**

Both facts can be individually correct, but an analyst usually needs the latest known management view. A workflow that extracts every version correctly can still mislead if synthesis does not understand which version supersedes another.

**Design response**

- explicit adjustment / update / revision language is treated as a current-state relationship rather than a simple numeric difference;
- synthesis should state the latest known value and the prior value it replaced;
- if the ordering cannot be established from the material, the output should say that multiple versions exist and require review rather than selecting one as current;
- the issue-only verifier now checks for stale values presented as the current state.

**Current status**

Added as a Demo regression target and synthesis / verifier rule.

---

## 13. Resolved change incorrectly promoted to a Flag

**Observed failure**

The material clearly showed:

> 管理层先预计 2026 年营收 3 亿元，随后将目标调整为 3.2 亿元。

The Matrix correctly resolved the current state to 3.2 亿元, but the workflow still created a Research Flag merely because a revision had occurred.

**Why it matters**

A historical revision is not automatically an unresolved research problem. If the latest state and direction of change are clear, promoting it into Flags creates unnecessary analyst work.

**Design response**

Research Flags now follow a stricter contract:

> **Material + Unresolved + Actionable**

A resolved revision or normal timeline progression stays in the Matrix. Only an unresolved version question, material conflict, scope/definition gap or material evidence gap becomes a Flag.

---

## 14. Overlapping categories treated as an arithmetic residual

**Observed failure pattern**

The material disclosed:

> 11 项核心专利

> 其中 5 项为合作开发

> 其中 3 项仍处于申请或开发阶段

A tempting but unsupported inference is:

> 11 - 5 - 3 = 3 项为公司独立持有且已授权专利

**Why it matters**

The arithmetic is valid only if “co-developed” and “pending/developing” are mutually exclusive categories. The material does not establish that. Some co-developed patents may also be pending, so the set relationship is unknown.

**Design response**

- do not infer a residual category unless the source explicitly establishes mutually exclusive and exhaustive classes;
- Matrix records the disclosed counts and the unresolved set relationship;
- when the gap is material to the investment thesis, create a Flag that asks the missing research question rather than inventing an answer.

The synthetic Demo now uses this as the primary Research Flag:

> How many of the 11 core patents are both independently controlled by the company and already granted?

---

## 15. PDF formatting caused false evidence-review warnings

**Observed failure**

A smoke test extracted correct facts from PDF text, but 9 of 11 facts were marked for review because source evidence had different line breaks, punctuation or date formatting from the parsed page text. Examples included `2021年5月` vs. `2021.05` and evidence fragments joined with semicolons.

**Why it matters**

A brittle exact-substring validator can suppress valid executive summaries, flood the Matrix with warning states and make the reliability layer itself less reliable.

**Design response**

- normalize Unicode, whitespace and punctuation before anchor matching;
- canonicalize dates before numeric comparison;
- allow evidence assembled from multiple supported text fragments instead of requiring one exact contiguous substring;
- label remaining failures as evidence-anchor warnings, not Research Flags.

---

## 16. Partial smoke-test coverage created false missing-information Flags

**Observed failure**

A representative 5-unit test surfaced Flags such as missing financing amounts or third-party validation even though the other 28 units had not been analyzed.

**Why it matters**

“Not observed in the sample” is not evidence that a document does not disclose the information.

**Design response**

- smoke mode explicitly tells synthesis that the evidence scope is partial;
- absence-based `material_evidence_gap` Flags are suppressed in partial-scope runs;
- structural ambiguity, explicit conflicts and definition/scope gaps can still be tested in smoke mode.

---

## Evaluation principles

The project is evaluated on more than fluent output.

Useful questions include:

- Did attribution survive?
- Can every important summary statement be traced to evidence?
- Were historical facts and projections kept distinct?
- Did the model add unsupported numbers or qualifiers?
- Did it confuse an application scenario with actual traction?
- Did it flag normal timeline changes as conflicts?
- Did synthesis preserve material caveats that change the interpretation of a headline fact?
- When a value was explicitly revised, did the current-state summary use the updated version rather than a stale one?
- How much of the original material still needs to be read?
- How many false-positive Research Flags were created?
- Does every Research Flag represent a material, unresolved and actionable research question?
- Did the workflow avoid residual arithmetic across categories whose overlap is unknown?
- Did valid PDF evidence survive harmless line-break, punctuation and date-format differences?
- In smoke mode, did the workflow avoid treating unobserved pages as proof of missing disclosure?
- What are the latency and API-cost bottlenecks?
- Did a pipeline change regress any known failure case?

These cases are kept as product-design evidence and future regression tests rather than hidden as embarrassing mistakes.
