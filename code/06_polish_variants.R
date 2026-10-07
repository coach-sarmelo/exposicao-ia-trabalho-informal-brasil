# =============================================================================
# Script:  06_polish_variants.R
# Author:  Marcelo Moura Freire
# Purpose: Robustness extension (v1.2.0) — beyond-manuscript coefficient-
#          stability battery on the shipped extract:
#          P1  UF fixed effects; log/IHS income + zero-earner dummy;
#              education top-code indicator (16y ceiling)
#          P3  rating-variant theta (data/analysis/variants_scores.json);
#              theta=0 / theta=10 bounding of the 696 coverage-missing workers
#          P5  individual-level logit for S3
# Inputs:  data/analysis/{individual_microdata.csv, scores.json,
#          econometrics.json, variants_scores.json}
# Outputs: output/robustness_ext/{polish_coefficients.csv, polish_results.json,
#          fig_polish_forest.png, fig_polish_forest.pdf}
# Standard: AEA Data Editor Standard (DCAS). Canonical results (econometrics.json)
#          are NEVER overwritten: this script first gates exact reproduction of
#          S1–S3 at the shipped 4-decimal storage rounding, then adds variants.
# Run:     Rscript code/06_polish_variants.R   (standalone; ~1–2 min)
# =============================================================================

suppressPackageStartupMessages({
  library(data.table)
  library(fixest)
  library(jsonlite)
  library(ggplot2)
})

if (!exists("PROJECT_SEED", inherits = FALSE)) {
  set.seed(20260413L)  # provenance only: no stochastic step in this script
}

resolve_root <- function() {
  cands <- character(0)
  if (requireNamespace("here", quietly = TRUE)) cands <- c(cands, here::here())
  cands <- c(cands, getwd())
  # script location fallback: <pkg>/code/06_polish_variants.R -> package root
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

find_path <- function(relative_options) {
  for (opt in relative_options) {
    p <- file.path(root_dir, opt)
    if (file.exists(p)) return(p)
  }
  stop("ABORT: none of these inputs found: ", paste(relative_options, collapse = ", "))
}

AN <- file.path("data", "analysis")
var_path <- find_path(c(file.path("data", "output", "variants_scores.json"),
                        file.path(AN, "variants_scores.json")))

cat("== 06_polish_variants: loading inputs ==\n")
raw <- data.table::fread(file.path(root_dir, AN, "individual_microdata.csv"))
scores_json <- jsonlite::fromJSON(file.path(root_dir, AN, "scores.json"), simplifyVector = FALSE)
econ <- jsonlite::fromJSON(file.path(root_dir, AN, "econometrics.json"), simplifyVector = FALSE)
variants <- jsonlite::fromJSON(var_path, simplifyVector = FALSE)

# ---- 1. Replicate 02_clean.R data construction exactly ----------------------
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

# Extension variables
df[, schooling_top16 := as.numeric(years_of_study == 16L)]
df[, income_zero := as.numeric(income == 0L)]
df[, log_income := log(as.numeric(income))]
df[, ihs_income := log(as.numeric(income) + sqrt(as.numeric(income)^2 + 1))]

cat(sprintf("estimation sample: %d rows, %d occupation clusters (paper: 227629 / 122)\n",
            nrow(df), uniqueN(df$occupation)))

# ---- 2. Baseline replication gate --------------------------------------------
ctrl <- "age + age_sq + is_female + i(race, ref = \"1\")"

fit_s1 <- feols(as.formula(paste("exposure ~ years_of_study +", ctrl)),
                weights = ~weight, cluster = ~occupation, data = df)
fit_s2 <- feols(as.formula(paste("exposure ~ years_of_study + income_thousands +", ctrl)),
                weights = ~weight, cluster = ~occupation, data = df)
fit_s3a <- feols(as.formula(paste("informal_pct ~ exposure +", ctrl)),
                 weights = ~weight, cluster = ~occupation, data = df)
fit_s3 <- feols(as.formula(paste("informal_pct ~ exposure + years_of_study +", ctrl)),
                weights = ~weight, cluster = ~occupation, data = df)

shipped <- list(S1 = fit_s1, S2 = fit_s2, S3a = fit_s3a, S3 = fit_s3)
# econometrics.json stores coefficients/SEs rounded to 4 decimal places
# (verified: every value matches round(x, 4)); the gate therefore compares
# our full-precision estimates after applying the same storage rounding.
round4 <- function(x) round(as.numeric(x), 4L)
base_check <- lapply(names(shipped), function(k) {
  ref <- econ$specifications[[k]]$results_clustered_occupation
  m <- shipped[[k]]
  list(
    spec = k,
    max_abs_beta_diff = max(abs(round4(coef(m)) - round4(ref$beta))),
    max_abs_se_diff = max(abs(round4(se(m)) - round4(ref$se))),
    r2_diff = abs(as.numeric(ref$r_squared) - as.numeric(r2(m, "r2"))),
    n_diff = abs(as.integer(ref$n) - as.integer(nobs(m)))
  )
})
worst <- max(vapply(base_check, function(x) max(x$max_abs_beta_diff, x$max_abs_se_diff), numeric(1)))
cat(sprintf("baseline gate (4-decimal storage rounding): worst diff = %.3e\n", worst))
if (worst > 1e-9) stop("ABORT: baseline does not reproduce shipped results; variants would be uninterpretable")

# ---- 3. Helper ---------------------------------------------------------------
grab <- function(m, focal, label, family, note = NA_character_, ncl = uniqueN(df$occupation)) {
  data.table(
    label = label, family = family, focal = focal,
    est = as.numeric(coef(m)[focal]), se = as.numeric(se(m)[focal]),
    p = as.numeric(pvalue(m)[focal]), r2 = as.numeric(r2(m, "r2")),
    n = as.integer(nobs(m)), n_clusters = as.integer(ncl), note = note
  )
}

# ---- 4. P1: UF FE / income functional form / education top-code --------------
mods <- list()

mods$S1_uf <- feols(exposure ~ years_of_study + age + age_sq + is_female + i(race, ref = "1") | uf,
                    weights = ~weight, cluster = ~occupation, data = df)
mods$S3_uf <- feols(informal_pct ~ exposure + years_of_study + age + age_sq + is_female + i(race, ref = "1") | uf,
                    weights = ~weight, cluster = ~occupation, data = df)

mods$S1_top16 <- feols(exposure ~ years_of_study + schooling_top16 + age + age_sq + is_female + i(race, ref = "1"),
                       weights = ~weight, cluster = ~occupation, data = df)
mods$S3_top16 <- feols(informal_pct ~ exposure + years_of_study + schooling_top16 + age + age_sq + is_female + i(race, ref = "1"),
                       weights = ~weight, cluster = ~occupation, data = df)
mods$S1_uf_top16 <- feols(exposure ~ years_of_study + schooling_top16 + age + age_sq + is_female + i(race, ref = "1") | uf,
                          weights = ~weight, cluster = ~occupation, data = df)

# income functional form (S2 family)
mods$S2_log <- feols(exposure ~ years_of_study + log_income + age + age_sq + is_female + i(race, ref = "1"),
                     weights = ~weight, cluster = ~occupation, data = df[income_zero == 0L])
mods$S2_ihs <- feols(exposure ~ years_of_study + ihs_income + income_zero + age + age_sq + is_female + i(race, ref = "1"),
                     weights = ~weight, cluster = ~occupation, data = df)
mods$S2_ihs_uf <- feols(exposure ~ years_of_study + ihs_income + income_zero + age + age_sq + is_female + i(race, ref = "1") | uf,
                        weights = ~weight, cluster = ~occupation, data = df)

# ---- 5. P3a: rating-variant theta --------------------------------------------
variant_cols <- c("dv_rating_alpha", "dv_rating_gamma",
                  "human_rating_alpha", "human_rating_beta", "human_rating_gamma")
g <- variants$groups
codes <- names(g)
vmap <- lapply(c("baseline" = "dv_rating_beta", setNames(variant_cols, variant_cols)), function(col) {
  v <- vapply(g, function(x) x[[col]], numeric(1)); names(v) <- codes; v
})
for (v in variant_cols) {
  df[, paste0("exposure_", v) := vmap[[v]][occupation]]
  mods[[paste0("S1_", v)]] <- feols(
    as.formula(paste0("exposure_", v, " ~ years_of_study + ", ctrl)),
    weights = ~weight, cluster = ~occupation, data = df)
  mods[[paste0("S3_", v)]] <- feols(
    as.formula(paste0("informal_pct ~ exposure_", v, " + years_of_study + ", ctrl)),
    weights = ~weight, cluster = ~occupation, data = df)
}

# ---- 6. P3b: theta bounding for the 696 coverage-missing workers -------------
# Build the FULL sample (n = 228,325): complete cases on everything EXCEPT
# exposure, so the 696 coverage-missing workers stay in and receive the bound.
df_full <- as.data.table(raw)
df_full[, occupation := as.character(occupation)]
df_full[, miss_cov := is.na(scores_map[occupation])]
req_no_exp <- setdiff(req_cols, "exposure")
df_full <- df_full[complete.cases(df_full[, ..req_no_exp])]
df_full[, exposure := scores_map[occupation]]
df_full[, age := as.numeric(age)]; df_full[, age_sq := age^2]
df_full[, is_female := as.numeric(sex == 2L)]; df_full[, race := factor(race)]
df_full[, informal_pct := as.numeric(informal) * 100.0]
n_b696 <- sum(df_full$miss_cov)
cat(sprintf("bounding sample: %d rows incl. %d coverage-missing workers, %d clusters\n",
            nrow(df_full), n_b696, uniqueN(df_full$occupation)))

df_full[, exposure := fifelse(miss_cov, 0, exposure)]   # bound: theta = 0
mods$S1_bound0 <- feols(exposure ~ years_of_study + age + age_sq + is_female + i(race, ref = "1"),
                        weights = ~weight, cluster = ~occupation, data = df_full)
mods$S3_bound0 <- feols(informal_pct ~ exposure + years_of_study + age + age_sq + is_female + i(race, ref = "1"),
                        weights = ~weight, cluster = ~occupation, data = df_full)
df_full[miss_cov == TRUE, exposure := 10]               # bound: theta = 10
mods$S1_bound10 <- feols(exposure ~ years_of_study + age + age_sq + is_female + i(race, ref = "1"),
                         weights = ~weight, cluster = ~occupation, data = df_full)
mods$S3_bound10 <- feols(informal_pct ~ exposure + years_of_study + age + age_sq + is_female + i(race, ref = "1"),
                         weights = ~weight, cluster = ~occupation, data = df_full)

# ---- 7. P5: S3 logit (functional form) ---------------------------------------
mods$S3_logit <- feglm(informal ~ exposure + years_of_study + age + age_sq + is_female + i(race, ref = "1"),
                       family = binomial("logit"), weights = ~weight,
                       cluster = ~occupation, data = df)

# ---- 8. Collect ---------------------------------------------------------------
focal_for <- function(lbl) {
  v <- sub("^(S1|S3)_", "", lbl)
  if (v %in% variant_cols) {
    # S1_* variants: the variant theta is the OUTCOME -> focal is schooling.
    # S3_* variants: the variant theta is the REGRESSOR -> focal is the variant.
    return(if (grepl("^S1", lbl)) "years_of_study" else paste0("exposure_", v))
  }
  if (grepl("^S3", lbl)) return("exposure")
  "years_of_study"
}
notes <- c(
  S1_uf = "P1: + 27 UF fixed effects", S3_uf = "P1: + 27 UF fixed effects",
  S1_top16 = "P1: + schooling top-code (16y) indicator", S3_top16 = "P1: + schooling top-code (16y) indicator",
  S1_uf_top16 = "P1: UF FE + top-code indicator",
  S2_log = "P1: log income, positive earners only", S2_ihs = "P1: IHS income + zero-earner dummy (full sample)",
  S2_ihs_uf = "P1: IHS income + zero dummy + UF FE",
  S1_bound0 = "P3b: 696 coverage-missing set to theta=0 (n incl. 696)", S3_bound0 = "P3b: theta=0 bound",
  S1_bound10 = "P3b: 696 set to theta=10", S3_bound10 = "P3b: theta=10 bound",
  S3_logit = "P5: logit (log-odds; AME not reported)"
)

est_list <- list(
  grab(fit_s1, "years_of_study", "S1 (baseline)", "S1: d(exposure)/d(schooling)", "shipped specification"),
  grab(fit_s2, "years_of_study", "S2 (baseline: income in levels)", "S1: d(exposure)/d(schooling)", "shipped specification"),
  grab(fit_s3a, "exposure", "S3a (baseline, no schooling)", "S3: d(informality pp)/d(exposure)", "shipped specification"),
  grab(fit_s3, "exposure", "S3 (baseline)", "S3: d(informality pp)/d(exposure)", "shipped specification")
)
for (lbl in names(mods)) {
  foc <- focal_for(lbl)
  nt <- ifelse(is.na(notes[lbl]), paste0("P3a: theta = ", sub("^(S1|S3)_", "", lbl)), notes[lbl])
  ncl <- if (grepl("bound", lbl)) uniqueN(df_full$occupation) else uniqueN(df$occupation)
  e <- tryCatch(grab(mods[[lbl]], foc, lbl, if (grepl("^S3", lbl)) "S3: d(informality pp)/d(exposure)" else "S1: d(exposure)/d(schooling)", nt, ncl),
                error = function(e) NULL)
  if (!is.null(e)) est_list[[length(est_list) + 1L]] <- e
}
est <- rbindlist(est_list)
est[, ci_lo := est - 1.96 * se]
est[, ci_hi := est + 1.96 * se]

# ---- 9. Concordance across rating variants (occupation-level Spearman) -------
occ_tab <- data.table(code = codes)
for (nm in names(vmap)) occ_tab[, (nm) := vmap[[nm]][code]]
spear <- cor(occ_tab[, -"code"], method = "spearman")
wconc <- sapply(variant_cols, function(v) {
  d <- df[!is.na(get(paste0("exposure_", v)))]
  x <- d$exposure; y <- d[[paste0("exposure_", v)]]; w <- d$weight
  mx <- sum(w * x) / sum(w); my <- sum(w * y) / sum(w)
  sum(w * (x - mx) * (y - my)) / sqrt(sum(w * (x - mx)^2) * sum(w * (y - my)^2))
})

disp_sd <- vapply(g, function(x) x$disp_sd_beta, numeric(1))
fallback_n <- sum(vapply(g, function(x) isTRUE(x$fallback_simple), logical(1)))

# ---- 10. Write outputs ---------------------------------------------------------
ext_dir <- file.path(root_dir, "output", "robustness_ext")
dir.create(ext_dir, recursive = TRUE, showWarnings = FALSE)
fwrite(est, file.path(ext_dir, "polish_coefficients.csv"))

results <- list(
  meta = list(
    purpose = "robustness extension v1.2.0: P1 (UF FE, income form, top-code), P3 (rating variants, bounding), P5 (logit)",
    baseline_gate_max_diff = worst,
    n_estimation = nrow(df), n_occupation_clusters = uniqueN(df$occupation),
    n_coverage_missing = n_b696, n_fallback_simple_groups = fallback_n,
    dispersion_mean_sd = mean(disp_sd), dispersion_max_sd = max(disp_sd),
    deterministic = TRUE, seed_note = "no stochastic step; paper seed 20260413 provenance only",
    original_results_canonical = "data/analysis/econometrics.json"
  ),
  baseline_check = base_check,
  estimates = as.list(est),
  spearman_occupation_level = spear,
  worker_weighted_pearson_vs_baseline = wconc
)
write_json(results, file.path(ext_dir, "polish_results.json"), auto_unbox = TRUE, pretty = TRUE, na = "null")

# forest figure
est[, label := factor(label, levels = rev(label))]
p <- ggplot(est[!label %in% c("S3 logit")], aes(x = est, y = label, color = grepl("baseline", label, fixed = TRUE) | label == "S3a (baseline, no schooling)")) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "grey55") +
  geom_pointrange(aes(xmin = ci_lo, xmax = ci_hi), linewidth = 0.4) +
  facet_wrap(~family, scales = "free") +
  scale_color_manual(values = c(`FALSE` = "#1f77b4", `TRUE` = "#444444"), guide = "none") +
  labs(title = "Coefficient stability across specification variants (robustness extension v1.2.0)",
       subtitle = "95% CIs, occupation-clustered SEs, V1028-weighted (logit model reported separately: different scale)",
       x = "Coefficient (95% CI)", y = NULL) +
  theme_minimal(base_size = 10)
ggsave(file.path(ext_dir, "fig_polish_forest.png"), p, width = 9.5, height = 7, dpi = 200)
ggsave(file.path(ext_dir, "fig_polish_forest.pdf"), p, width = 9.5, height = 7)

cat("\n== headline movements vs S1 baseline (beta_schooling) ==\n")
base_s1 <- est[label == "S1 (baseline)"]$est
for (i in which(est$family == "S1: d(exposure)/d(schooling)" & grepl("^S1", est$label) & est$label != "S1 (baseline)")) {
  b <- est[i]
  cat(sprintf("  %-26s %+.4f -> %+.4f  (%+.1f%% in |beta|)\n", b$label, base_s1, b$est, 100 * (abs(b$est) - abs(base_s1)) / abs(base_s1)))
}
cat("\n== headline movements vs S3 baseline (beta_exposure, informal %p) ==\n")
base_s3 <- est[label == "S3 (baseline)"]$est
for (i in which(est$family == "S3: d(informality pp)/d(exposure)" & grepl("^S3", est$label) & est$label != "S3 (baseline)" & est$label != "S3a (baseline, no schooling)")) {
  b <- est[i]
  if (b$label == "S3_logit") {
    cat(sprintf("  %-26s %+.4f -> %+.4f  (log-odds per unit theta - different scale, not comparable)\n", b$label, base_s3, b$est))
  } else {
    cat(sprintf("  %-26s %+.4f -> %+.4f  (%+.1f%% in |beta|)\n", b$label, base_s3, b$est, 100 * (abs(b$est) - abs(base_s3)) / abs(base_s3)))
  }
}
cat("\n== S2 income functional form (beta_schooling) ==\n")
for (lbl in c("S1 (baseline)", "S2 (baseline: income in levels)", "S2_log", "S2_ihs", "S2_ihs_uf")) {
  b <- est[label == lbl]
  cat(sprintf("  %-32s %+.4f\n", lbl, b$est))
}
cat(sprintf("\nDone. Outputs in %s\n", ext_dir))
