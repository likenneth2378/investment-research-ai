# Failure Cases

This file records product-level failures observed during development. It intentionally excludes ordinary beginner coding mistakes such as syntax errors, indentation errors, or local path issues.

The purpose is to show how observed failures changed the product design.

---

## 1. Attribution stripping

**Observed behavior**

Source:

> 公司称目前拥有11项核心专利。

Model output in one test:

> 公司拥有11项核心专利。

**Why it matters**

The model removed the attribution layer. A company-reported statement was turned into an apparently objective fact.

In investment research, this can materially increase the perceived strength of evidence.

**Hypothesis**

If claim extraction focuses only on producing a concise statement, the model may compress away wording such as “公司称”, “管理层表示”, or “据公司材料”.

**Design response**

- Added `source_text` as an explicit evidence anchor.
- Made attribution preservation a core design requirement.
- Future versions should extract both the specific attribution and the normalized claim rather than replacing the original source wording.

**Current status**

Partially mitigated in later prompt tests, but not yet systematically benchmarked.

---

## 2. Historical fact misclassified as projection

**Observed behavior**

Source:

> 2025年实现营收1.26亿元，同比增长186%。

The model classified this as:

`Projection`

A separate statement such as:

> 2026年预计营收达到3亿元。

is a genuine projection.

**Why it matters**

Historical performance and forward-looking guidance play different roles in investment analysis. Misclassifying a completed result as a forecast can distort later filtering, comparison, or review.

**Hypothesis**

The model may rely too heavily on the financial context of the sentence and fail to distinguish completed-period language from forward-looking language.

**Design response**

- Preserved this as a baseline semantic failure case.
- Avoid treating model-generated `evidence_status` as ground truth.
- Future evaluation should explicitly test historical vs projected statements.

**Current status**

Open.

---

## 3. Measurable performance claim misclassified as projection or marketing

**Observed behavior**

Source:

> 公司自主开发的EMS能源管理系统可以使储能项目综合收益提升约15%。

The model classified this as `Projection` in one test and as a subjective / marketing-style claim in another.

**Why it matters**

The statement is promotional in context, but it is also a measurable performance claim. The key research question is not whether it sounds promotional, but whether there is sufficient evidence to support the claimed 15% improvement.

**Hypothesis**

A coarse taxonomy can encourage the model to classify by tone instead of by evidentiary structure.

**Design response**

The working rule became:

- measurable but unsupported performance claim → `Unverified`
- explicitly forward-looking claim → `Projection`
- non-measurable positioning language → `Subjective / Marketing`

**Current status**

Taxonomy revised conceptually; not yet reliably enforced by the current prototype.

---

## 4. Valid-looking model output that is not machine-valid JSON

**Observed behavior**

Across several model/provider tests, structured output sometimes contained:

- Markdown code fences
- malformed quote escaping
- trailing commas
- unterminated strings
- truncated JSON
- empty output

**Why it matters**

A response can look readable to a human but still fail at `json.loads()`. In a batch research workflow, one malformed response can interrupt processing or silently remove records.

**Hypothesis**

Prompting for JSON alone does not guarantee machine-valid structured output, especially when models approach output or reasoning limits.

**Design response**

- Added JSON parsing as an explicit validation step.
- Used `try / except JSONDecodeError` during testing so one bad record would not necessarily terminate the entire batch.
- Treated schema validity as a separate evaluation dimension from semantic quality.

**Current status**

Partially mitigated. Robust schema validation is not yet implemented.

---

## 5. Long-input instability

**Observed behavior**

Short single-statement tests frequently returned complete structured output, while longer full-document inputs were more likely to produce:

- truncation
- incomplete reasoning
- malformed JSON
- empty output

**Why it matters**

Investment materials are usually multi-page and multi-document. A system that works only on short isolated sentences is not useful for a real research workflow.

**Hypothesis**

Longer inputs increase both reasoning load and structured-output length, making completion reliability worse for some models and providers.

**Design response**

Moved away from relying on one-shot full-document extraction and toward a chunked workflow.

However, chunking cannot be too aggressive because context can be lost. For example:

> 公司称：
>
> 已完成27个工商业储能项目。

If those lines are processed separately, attribution may be lost.

The next design step is therefore **context-preserving chunking**, not simple line-by-line extraction.

**Current status**

Observed and documented. Context-preserving chunk extraction is the next implementation milestone.

---

## 6. Cross-document discrepancy as a target failure mode

This case has not yet been automatically detected by the system, but the synthetic test files already contain examples designed for the next milestone.

Source A:

> 公司已完成27个工商业储能项目。

Source B:

> 公司称已完成30个工商业储能项目。

Another pair:

> 公司预计2026年营收达到3亿元。

vs.

> 公司预计2026年营收达到3.2亿元。

**Why it matters**

The correct response is not to decide which number is true automatically. The useful behavior is to surface that the claims appear to refer to the same topic but differ in value, so a researcher can check timing, scope, or definition.

**Design target**

Future versions should:

1. group semantically similar claims across documents;
2. surface potentially conflicting values;
3. retain both original source texts and locations;
4. flag the discrepancy for human review;
5. avoid generating an investment conclusion automatically.

**Current status**

Not yet implemented. This is one of the main product-value milestones after semantic claim extraction is restored.

---

## Evaluation principle

The project should not be evaluated only on whether an LLM can produce fluent output.

A more useful evaluation asks:

- Did attribution survive extraction?
- Can each claim be traced back to its original evidence?
- Are historical facts distinguished from forecasts?
- Are measurable but unsupported claims treated as evidence problems rather than merely “marketing”?
- Is the output machine-valid and schema-complete?
- Can the workflow surface cross-document discrepancies without inventing a conclusion?

These failure cases are kept as regression tests and product-design evidence rather than hidden as implementation mistakes.
