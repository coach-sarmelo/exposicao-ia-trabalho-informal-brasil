---
paths:
  - ".agents/agents/**/agent.md"
  - ".agents/skills/**/SKILL.md"
  - ".claude/agents/**/agent.md"
  - ".claude/skills/**/SKILL.md"
---

# Per-Agent Model Routing (Gemini 3.1 Pro / 3.7 Flash - Maximum Effort)

**Match model tier to the cognitive demand of the work, running at maximum effort level.** Reserve **Gemini 3.1 Pro** and **Gemini 3.7 Flash (High/Max Reasoning)** for high-judgment and analytical tasks; route mechanical execution to **Gemini 2.5 Flash**; run all models at **maximum reasoning/effort (`effort: max`)** to ensure maximum analytical rigor, complete mathematical verification, and zero-defect code and prose review.

## The 70/20/10 Gemini Routing Pattern (Maximum Effort)

| Share | Tier | Model & Thinking Level | Use for |
|---:|---|---|---|
| ~70% | **Mechanical** | **Gemini 2.5 Flash** (`effort: max`) | Mechanical execution — file renames, citation-format conversion, TikZ extraction, bib validation, proofread-fix application, regex/search-and-replace, simple grep lookups |
| ~20% | **Review & Critique** | **Gemini 3.7 Flash** (`effort: max`) | Review and critique — `r-reviewer`, `slide-auditor`, `proofreader`, `quarto-fixer`, `humanize-auditor`, `beamer-translator` |
| ~10% | **High-Judgment** | **Gemini 3.1 Pro** / **Gemini 3.7 Flash** (`effort: max`) | High-judgment and adversarial work — `editor`, `methods-referee`, `domain-referee`, `claim-verifier`, `quarto-critic`, `tikz-reviewer`, `domain-reviewer`, `verifier` for hard gates |

Set per-agent via `model:` and `effort:` in the agent's YAML frontmatter:

```yaml
---
name: methods-referee
model: gemini-3.1-pro
effort: max
---
```

Set per-skill via the same fields in `SKILL.md` frontmatter.

## The Effort Axis: Maximum Reasoning Configured

All models are set to **maximum effort (`effort: max`)**:
- **Gemini 3.1 Pro (`effort: max`)**: Maximum depth for theoretical proofs (`02_modelo.tex`, `apendice.tex`), identification strategy vetting, econometric mediation analysis, and final editorial gates.
- **Gemini 3.7 Flash (`effort: max`)**: Extended thinking for code auditing, visual layout checks, de-AI review, and cross-artifact parity verification.
- **Gemini 2.5 Flash (`effort: max`)**: Maximum precision for mechanical AST modifications, bibliographic key resolution, and script execution.

## Routing Recipe per Task Type (Max Effort)

### Mechanical (Gemini 2.5 Flash · `effort: max`)

- **TikZ $	o$ SVG extraction** (`extract-tikz` execution agent).
- **Bib formatting / citation rewrites** (`validate-bib` mechanical fix path).
- **Quarto fixer applying critic's diff** (`quarto-fixer` — separate from `quarto-critic`).
- **Proofread fix application** (when the fix is direct string replacement).
- **File rename / search-and-replace operations.**

### Review & Critique (Gemini 3.7 Flash · `effort: max`)

- **R code review** (`r-reviewer`).
- **Slide layout audit** (`slide-auditor`).
- **Proofread inspection** (`proofreader`).
- **Quarto fix application** when driven by `quarto-critic` edits.
- **AI-voice audit** (`humanize-auditor`).
- **Beamer $\longleftrightarrow$ Quarto translation** (`beamer-translator`).

### High-Judgment (Gemini 3.1 Pro / Gemini 3.7 Flash · `effort: max`)

- **Editor for `/review-paper --peer`** (`editor`).
- **Both referee agents** (`domain-referee`, `methods-referee`).
- **Claim verifier in fresh-context mode** (`claim-verifier`).
- **Quarto critic** (`quarto-critic`) — adversarial parity QA requires spatial and visual acuity.
- **TikZ reviewer** (`tikz-reviewer`) — measurement-rule enforcement requires precise spatial reasoning.
- **Domain reviewer** (`domain-reviewer`).
- **Verifier** (`verifier`) when gating non-trivial commits and release packages.

## Cross-References

- [`.agents/plugins/academic-workflow/rules/cross-artifact-review.md`](cross-artifact-review.md) — paper $\longleftrightarrow$ code dependency graph.
- [`.agents/plugins/academic-workflow/rules/post-flight-verification.md`](post-flight-verification.md) — Chain-of-Verification (CoVe) and forked verifier protocols.
- [`.agents/plugins/academic-workflow/references/orchestration-schemas.md`](../references/orchestration-schemas.md) — structured `FINDING` and `SCORECARD` schemas.
