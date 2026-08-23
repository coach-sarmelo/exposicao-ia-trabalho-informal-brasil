<!-- CURRENT: Gemini 3.1 Pro | Gemini 3.7 Flash | Gemini 2.5 Flash -->

# Current Gemini Model Versions (single source of truth)

**Last verified against Google Antigravity docs:** 2026-08-23

This file is the **one place** that names current Gemini model tiers in the Antigravity (agy) ecosystem, configured at **maximum effort (`effort: max`)**.

| Tier | Current Version | Model ID / Selection | Default Effort | Notes |
|------|-----------------|----------------------|----------------|-------|
| Deep Reasoning & High Judgment | **Gemini 3.1 Pro** | `gemini-3.1-pro` | `effort: max` | Deepest reasoning, theoretical proof derivations, editorial synthesis, identification validation, adversarial peer review. |
| Workhorse & Review | **Gemini 3.7 Flash** | `gemini-3.7-flash` | `effort: max` | Maximum thinking budget for standard review, code inspection, slide audits, humanize / voice checks, parity translation. |
| Mechanical & Fast | **Gemini 2.5 Flash** | `gemini-2.5-flash` | `effort: max` | Ultra-fast execution with full precision: file renames, regex search-and-replace, TikZ extraction, bib validation, direct diff application. |

## Effort Configuration

- All models are pinned to **maximum reasoning effort (`effort: max`)** across all workflow pipelines to guarantee maximum analytical depth and zero-defect review.
