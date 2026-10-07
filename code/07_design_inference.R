# =============================================================================
# Script:  07_design_inference.R
# Author:  Marcelo Moura Freire
# Purpose: Robustness extension (v1.2.0) — survey-design inference battery for
#          S1/S2/S3a/S3 on the design-variable extract
#          (data/analysis/individual_microdata_design.csv: UPA = PSU,
#          Estrato = stratum, V1008, V2003).
#          Battery: occupation-clustered (gate vs econometrics.json), PSU
#          cluster, two-way occupation x UPA, and survey-linearized (svyglm,
#          strata x UPA, nest). Also Kish ESS and the design effect of the
#          weighted informality rate.
# Inputs:  data/analysis/{individual_microdata_design.csv, scores.json,
#          econometrics.json} (regenerate the extract with
#          scripts/build_design_extract.py if absent)
# Outputs: output/robustness_ext/p2_results.json
# Standard: AEA Data Editor Standard (DCAS). Canonical results are never
#          overwritten; the occupation-clustered baseline must first reproduce
#          econometrics.json exactly (4-decimal storage rounding).
# Run:     Rscript code/07_design_inference.R   (standalone; requires the
#          survey package; ~1 min)
# =============================================================================

suppressPackageStartupMessages({
  library(data.table)
  library(fixest)
  library(jsonlite)
  library(survey)
})

resolve_root <- function() {
  cands <- character(0)
  if (requireNamespace("here", quietly = TRUE)) cands <- c(cands, here::here())
  cands <- c(cands, getwd())
  # script location fallback: <pkg>/code/07_design_inference.R -> package root
  ca <- commandArgs(trailingOnly = FALSE)
  fa <- grep("^--file=", ca, value = TRUE)
  if (length(fa)) cands <- c(cands, dirname(dirname(normalizePath(sub("^--file=", "", fa[1]), winslash = "/"))))
  for (r in unique(cands)) {
    if (file.exists(file.path(r, "data", "analysis", "scores.json"))) return(r)
  }
  stop("ABORT: package root not found (expected data/analysis/scores.json); ",
       "run Rscript from the replication package root")
}
root_dir <- resolve_root()

AN <- file.path("data", "analysis")
design_csv <- file.path(root_dir, AN, "individual_microdata_design.csv")
if (!file.exists(design_csv)) {
  design_csv <- file.path(root_dir, "data", "output", "individual_microdata_design.csv")
}
if (!file.exists(design_csv)) {
  stop("ABORT: individual_microdata_design.csv not found. Run: ",
       "python scripts/build_design_extract.py (downloads PNADC_012026.zip, 228.6 MB)")
}

cat("== 07_design_inference: loading design extract ==\n")
raw <- fread(design_csv,
             colClasses = list(character = c("occupation", "sex", "race",
                                             "upa", "estrato", "v1008", "v2003")))
scores_json <- fromJSON(file.path(root_dir, AN, "scores.json"), simplifyVector = FALSE)
econ <- fromJSON(file.path(root_dir, AN, "econometrics.json"), simplifyVector = FALSE)

# ---- replicate 02_clean.R ----------------------------------------------------
scores_map <- unlist(lapply(names(scores_json), function(k) {
  if (k != "_meta" && !is.null(scores_json[[k]]$exposure)) {
    val <- scores_json[[k]]$exposure; names(val) <- k; return(val)
  }
  NULL
}))
df <- as.data.table(raw)
df[, occupation := as.character(occupation)]
df[, exposure := scores_map[occupation]]
req_cols <- c("exposure", "years_of_study", "income", "informal", "uf",
              "occupation", "weight", "age", "sex", "race")
df <- df[complete.cases(df[, ..req_cols])]
df[, age := as.numeric(age)]
df[, age_sq := age^2]
df[, is_female := as.numeric(sex == 2L)]
df[, race := factor(race)]
df[, income_thousands := as.numeric(income) / 1000.0]
df[, informal_pct := as.numeric(informal) * 100.0]

cat(sprintf("estimation sample: %d rows | %d occupation clusters | %d UPAs | %d strata\n",
            nrow(df), uniqueN(df$occupation), uniqueN(df$upa), uniqueN(df$estrato)))

kish <- sum(df$weight)^2 / sum(df$weight^2)
cat(sprintf("Kish ESS (estimation sample): %.0f\n", kish))

ctrl <- "age + age_sq + is_female + i(race, ref = \"1\")"
f_s1 <- as.formula(paste("exposure ~ years_of_study +", ctrl))
f_s2 <- as.formula(paste("exposure ~ years_of_study + income_thousands +", ctrl))
f_s3a <- as.formula(paste("informal_pct ~ exposure +", ctrl))
f_s3 <- as.formula(paste("informal_pct ~ exposure + years_of_study +", ctrl))

# ---- gate: occupation-clustered baseline vs shipped results ------------------
fit_gate <- feols(f_s3, weights = ~weight, cluster = ~occupation, data = df)
ref <- econ$specifications$S3$results_clustered_occupation
gate_diff <- max(abs(round(as.numeric(coef(fit_gate)), 4) - round(as.numeric(ref$beta), 4)),
                 abs(round(as.numeric(se(fit_gate)), 4) - round(as.numeric(ref$se), 4)))
cat(sprintf("gate (S3, occupation-clustered, 4-dec storage rounding): max diff = %.1e\n", gate_diff))
if (gate_diff > 1e-9) stop("ABORT: design extract baseline does not reproduce shipped results")

# ---- clustering battery ------------------------------------------------------
run <- function(fml, cluster_expr, data = df) {
  feols(fml, weights = ~weight, cluster = cluster_expr, data = data)
}
specs <- list(S1 = f_s1, S2 = f_s2, S3a = f_s3a, S3 = f_s3)
focal <- c(S1 = "years_of_study", S2 = "years_of_study", S3a = "exposure", S3 = "exposure")

res <- list()
for (s in names(specs)) {
  foc <- focal[[s]]
  row_oc <- run(specs[[s]], ~occupation)
  row_psu <- run(specs[[s]], ~upa)
  row_two <- run(specs[[s]], ~occupation + upa)
  res[[s]] <- list(
    occupation = list(beta = unname(coef(row_oc)[foc]), se = unname(se(row_oc)[foc]),
                      p = unname(pvalue(row_oc)[foc]), ncl = uniqueN(df$occupation)),
    upa_psu    = list(beta = unname(coef(row_psu)[foc]), se = unname(se(row_psu)[foc]),
                      p = unname(pvalue(row_psu)[foc]), ncl = uniqueN(df$upa)),
    two_way    = list(beta = unname(coef(row_two)[foc]), se = unname(se(row_two)[foc]),
                      p = unname(pvalue(row_two)[foc]), ncl_oc = uniqueN(df$occupation),
                      ncl_upa = uniqueN(df$upa))
  )
  cat(sprintf("%-4s beta=%+.4f | se: occ %.4f -> psu %.4f (%+.0f%%) -> two-way %.4f (%+.0f%%)\n",
              s, res[[s]]$occupation$beta,
              res[[s]]$occupation$se, res[[s]]$upa_psu$se,
              100 * (res[[s]]$upa_psu$se / res[[s]]$occupation$se - 1),
              res[[s]]$two_way$se, 100 * (res[[s]]$two_way$se / res[[s]]$occupation$se - 1)))
}

# ---- design-based linearization (svyglm) -------------------------------------
cat("\n== svyglm (linearized, strata x UPA, nest; lonely PSU strata centered) ==\n")
# Some IBGE strata contain a single UPA (certainty units). Standard remedy:
# center those strata at the grand mean ("adjust"); count them for the report.
options(survey.lonely.psu = "adjust")
lonely <- df[, .(n_upa = uniqueN(upa)), by = estrato][n_upa == 1, .N]
cat(sprintf("strata with a single PSU: %d of %d (lonely.psu = adjust)\n", lonely, uniqueN(df$estrato)))
des <- svydesign(ids = ~upa, strata = ~estrato, weights = ~weight, nest = TRUE, data = df)
svy_res <- list()
for (s in c("S1", "S2", "S3a", "S3")) {
  # glm-based svyglm cannot parse fixest's i(); plain factor race gives the
  # identical model (reference level "1" = first level).
  f <- switch(s,
    S1  = exposure ~ years_of_study + age + age_sq + is_female + race,
    S2  = exposure ~ years_of_study + income_thousands + age + age_sq + is_female + race,
    S3a = informal_pct ~ exposure + age + age_sq + is_female + race,
    S3  = informal_pct ~ exposure + years_of_study + age + age_sq + is_female + race
  )
  m <- svyglm(f, design = des)
  sm <- summary(m)$coefficients
  foc <- focal[[s]]
  i <- which(rownames(sm) == foc)
  est <- sm[i, "Estimate"]; sel <- sm[i, "Std. Error"]; pv <- sm[i, 4]  # col 4: Pr(>|t|)
  svy_res[[s]] <- list(beta = unname(est), se = unname(sel), p = unname(pv))
  cat(sprintf("%-4s beta=%+.4f  linearized se=%.4f  (vs occupation-clustered %.4f, %+.0f%%)\n",
              s, est, sel, res[[s]]$occupation$se,
              100 * (sel / res[[s]]$occupation$se - 1)))
}

# DEFF for a headline proportion: weighted informality mean vs SRS
m_informal <- svymean(~informal_pct, des, deff = TRUE)
deff_informal <- deff(m_informal)
cat(sprintf("\nweighted informality: %.2f%% | design effect (informal_pct): %.3f\n",
            unname(coef(m_informal)), deff_informal))

out <- list(
  meta = list(
    purpose = "robustness extension v1.2.0: design-based inference battery",
    n = nrow(df), n_occupation = uniqueN(df$occupation), n_upa = uniqueN(df$upa),
    n_estrato = uniqueN(df$estrato), n_lonely_strata = lonely,
    kish_ess = kish, gate_max_diff = gate_diff, deff_informal_pct = unname(deff_informal),
    lonely_psu_option = "adjust",
    deterministic = TRUE
  ),
  clustering = res, svyglm = svy_res
)
ext_dir <- file.path(root_dir, "output", "robustness_ext")
dir.create(ext_dir, recursive = TRUE, showWarnings = FALSE)
write_json(out, file.path(ext_dir, "p2_results.json"), auto_unbox = TRUE, pretty = TRUE, digits = 8)
cat(sprintf("\n-> %s\n", file.path(ext_dir, "p2_results.json")))
