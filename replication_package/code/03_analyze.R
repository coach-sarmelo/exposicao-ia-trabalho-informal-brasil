# =============================================================================
# Script:  03_analyze.R
# Author:  Marcelo Moura Freire
# Purpose: Microeconometric estimation of S1–S4 and sensitivity battery R1–R7
# Inputs:  df (from 02_clean.R)
# Outputs: scripts/R/_outputs/results.rds, data/output/econometrics.json
# Standard: AEA Data Editor Standard (DCAS) / INV-1 through INV-12
# =============================================================================

if (!exists("df", inherits = FALSE)) {
  stop("03_analyze.R: df not found. Run 00_run_all.R first.")
}

suppressPackageStartupMessages({
  library(data.table)
  library(fixest)
  library(jsonlite)
})

root_dir <- if (requireNamespace("here", quietly = TRUE)) here::here() else getwd()
out_dir  <- if (exists("OUT_DIR", inherits = FALSE)) OUT_DIR else file.path(root_dir, "scripts", "R", "_outputs")
if (!dir.exists(out_dir)) dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

#' Extract model coefficients, clustered standard errors and metadata from feols
#'
#' @param model A fitted \code{fixest::feols} object.
#' @param n_clusters Integer, number of independent clusters.
#' @return A named list containing beta, se, p_value, r_squared, n, n_clusters, and names.
extract_feols <- function(model, n_clusters) {
  co <- coef(model)
  se <- se(model)
  pv <- pvalue(model)
  list(
    beta       = unname(as.numeric(co)),
    se         = unname(as.numeric(se)),
    p_value    = unname(as.numeric(pv)),
    r_squared  = as.numeric(r2(model, "r2")),
    n          = as.integer(nobs(model)),
    n_clusters = as.integer(n_clusters),
    names      = names(co)
  )
}

n_clusters_occ <- uniqueN(df$occupation)

# ---- 1. Primary Specifications (S1–S4) --------------------------------------
message("Fitting primary models S1–S4...")

# S1: Baseline Education Gradient
fit_s1 <- feols(
  exposure ~ years_of_study + age + age_sq + is_female + i(race, ref = "1"),
  weights = ~weight,
  cluster = ~occupation,
  data = df
)

# S2: Wage Control Gradient
fit_s2 <- feols(
  exposure ~ years_of_study + income_thousands + age + age_sq + is_female + i(race, ref = "1"),
  weights = ~weight,
  cluster = ~occupation,
  data = df
)

# S3a: Gross Informality Mediation
fit_s3a <- feols(
  informal_pct ~ exposure + age + age_sq + is_female + i(race, ref = "1"),
  weights = ~weight,
  cluster = ~occupation,
  data = df
)

# S3: Conditional Informality Mediation
fit_s3 <- feols(
  informal_pct ~ exposure + years_of_study + age + age_sq + is_female + i(race, ref = "1"),
  weights = ~weight,
  cluster = ~occupation,
  data = df
)

# S4: Regional Interaction (27 UFs LOO)
df_s4 <- df[!is.na(formality_loo)]
fit_s4 <- feols(
  exposure ~ years_of_study + years_x_formality + formality_loo + age + age_sq + is_female + i(race, ref = "1"),
  weights = ~weight,
  cluster = ~occupation,
  data = df_s4
)

b_form_s4 <- coef(fit_s4)["formality_loo"]
b_int_s4  <- coef(fit_s4)["years_x_formality"]
threshold_e_star <- if (abs(b_int_s4) > 1e-12) unname(-b_form_s4 / b_int_s4) else NA_real_

# ---- 2. Robustness Battery (R1–R7) ------------------------------------------
message("Fitting robustness battery R1–R7...")

# R1: Unweighted OLS
fit_r1 <- feols(
  exposure ~ years_of_study + age + age_sq + is_female + i(race, ref = "1"),
  cluster = ~occupation,
  data = df
)

# R4: Log-Transformed log(1 + theta)
fit_r4 <- feols(
  log(1 + exposure) ~ years_of_study + age + age_sq + is_female + i(race, ref = "1"),
  weights = ~weight,
  cluster = ~occupation,
  data = df
)

# R5: Winsorization (1%/99%)
p01 <- quantile(df$exposure, 0.01, na.rm = TRUE)
p99 <- quantile(df$exposure, 0.99, na.rm = TRUE)
df_winsor <- copy(df)
df_winsor[, exposure := pmin(pmax(exposure, p01), p99)]
fit_r5 <- feols(
  exposure ~ years_of_study + age + age_sq + is_female + i(race, ref = "1"),
  weights = ~weight,
  cluster = ~occupation,
  data = df_winsor
)

# R6: Exclude Top 1% Exposure
p99_exp <- quantile(df$exposure, 0.99, na.rm = TRUE)
df_no_p99 <- df[exposure <= p99_exp]
fit_r6 <- feols(
  exposure ~ years_of_study + age + age_sq + is_female + i(race, ref = "1"),
  weights = ~weight,
  cluster = ~occupation,
  data = df_no_p99
)

# R7: COD Major Group Exclusions (1–9) for both S1 and S3
df[, cod_grande_grupo := substr(occupation, 1L, 1L)]
grupos_cod <- sort(unique(df$cod_grande_grupo))
r7_subgroups <- vector("list", length(grupos_cod))
names(r7_subgroups) <- paste0("sem_grupo_", grupos_cod)

for (g in grupos_cod) {
  df_sub <- df[cod_grande_grupo != g]
  fit_sub <- feols(
    exposure ~ years_of_study + age + age_sq + is_female + i(race, ref = "1"),
    weights = ~weight,
    cluster = ~occupation,
    data = df_sub
  )
  fit_s3_sub <- feols(
    informal_pct ~ exposure + years_of_study + age + age_sq + is_female + i(race, ref = "1"),
    weights = ~weight,
    cluster = ~occupation,
    data = df_sub
  )
  r7_subgroups[[paste0("sem_grupo_", g)]] <- list(
    grupo_excluido = g,
    beta_schooling = as.numeric(coef(fit_sub)["years_of_study"]),
    se_schooling   = as.numeric(se(fit_sub)["years_of_study"]),
    p_schooling    = as.numeric(pvalue(fit_sub)["years_of_study"]),
    beta_s3_exp    = as.numeric(coef(fit_s3_sub)["exposure"]),
    se_s3_exp      = as.numeric(se(fit_s3_sub)["exposure"]),
    p_s3_exp       = as.numeric(pvalue(fit_s3_sub)["exposure"]),
    r_squared      = as.numeric(r2(fit_sub, "r2")),
    n              = as.integer(nobs(fit_sub)),
    n_clusters     = as.integer(uniqueN(df_sub$occupation))
  )
}

# ---- 3. Oster (2019) Bounding Calculation -----------------------------------
# Transition from S1 (baseline) to S2 (controlling for income)
b_s1  <- as.numeric(coef(fit_s1)["years_of_study"])
r2_s1 <- as.numeric(r2(fit_s1, "r2"))
b_s2  <- as.numeric(coef(fit_s2)["years_of_study"])
r2_s2 <- as.numeric(r2(fit_s2, "r2"))
r_max <- 1.3 * r2_s2

# Oster (2019, JBES): adjustment distance measures remaining variation relative to controlled model
delta_denom <- (b_s1 - b_s2) * (r_max - r2_s1)
r2_diff     <- r2_s2 - r2_s1
eps <- 1e-12

if (abs(delta_denom) > eps && abs(r2_diff) > eps) {
  delta_oster <- unname((b_s2 * r2_diff) / delta_denom)
  bstar_oster <- unname(b_s2 - (b_s1 - b_s2) * (r_max - r2_s1) / r2_diff)
} else {
  delta_oster <- NA_real_
  bstar_oster <- NA_real_
}

# ---- 4. Descriptive Pre-Aggregations for Self-Contained Tables 1 & 2 --------
calc_stats <- function(sub_df) {
  w <- sub_df$weight
  m_exp <- weighted.mean(sub_df$exposure, w, na.rm = TRUE)
  m_sch <- weighted.mean(sub_df$years_of_study, w, na.rm = TRUE)
  m_inc <- weighted.mean(sub_df$income, w, na.rm = TRUE)
  list(
    n_obs   = nrow(sub_df),
    pop_m   = sum(w, na.rm = TRUE) / 1e6,
    exp_m   = m_exp,
    exp_sd  = sqrt(sum(w * (sub_df$exposure - m_exp)^2, na.rm = TRUE) / sum(w, na.rm = TRUE)),
    sch_m   = m_sch,
    sch_sd  = sqrt(sum(w * (sub_df$years_of_study - m_sch)^2, na.rm = TRUE) / sum(w, na.rm = TRUE)),
    inc_m   = m_inc,
    inc_sd  = sqrt(sum(w * (sub_df$income - m_inc)^2, na.rm = TRUE) / sum(w, na.rm = TRUE)),
    fem_pct = weighted.mean(sub_df$is_female, w, na.rm = TRUE) * 100.0,
    age_m   = weighted.mean(sub_df$age, w, na.rm = TRUE)
  )
}

desc_stats <- list(
  total    = calc_stats(df),
  formal   = calc_stats(df[informal == 0L]),
  informal = calc_stats(df[informal == 1L])
)

occ_summary <- df[, .(
  exposure    = mean(exposure, na.rm = TRUE),
  schooling   = weighted.mean(years_of_study, weight, na.rm = TRUE),
  employment  = sum(weight, na.rm = TRUE) / 1e6,
  informality = weighted.mean(informal, weight, na.rm = TRUE) * 100.0,
  income      = weighted.mean(income, weight, na.rm = TRUE)
), by = occupation]
setorder(occ_summary, -employment)
top10_occ    <- head(occ_summary, 10L)
bottom10_occ <- tail(occ_summary, 10L)

#' Pack model into a compact summary list for fast serialization (<1KB per model)
#'
#' @param m A fitted \code{fixest::feols} object.
#' @return A compact list containing coefficients, standard errors, p-values, R2, and nobs.
pack_model <- function(m) {
  if (is.null(m)) return(NULL)
  list(
    coefficients = coef(m),
    se           = se(m),
    pvalue       = pvalue(m),
    coeftable    = coeftable(m),
    r2           = as.numeric(r2(m, "r2")),
    nobs         = as.integer(nobs(m))
  )
}

# ---- 5. Save RDS & Authoritative JSON Artifacts -----------------------------
results <- list(
  models = list(
    s1  = pack_model(fit_s1),
    s2  = pack_model(fit_s2),
    s3a = pack_model(fit_s3a),
    s3  = pack_model(fit_s3),
    s4  = pack_model(fit_s4),
    r1  = pack_model(fit_r1),
    r4  = pack_model(fit_r4),
    r5  = pack_model(fit_r5),
    r6  = pack_model(fit_r6)
  ),
  r7_subgroups     = r7_subgroups,
  oster            = list(delta = delta_oster, bstar = bstar_oster, r_max = r_max, b_s1 = b_s1, b_s2 = b_s2),
  threshold_e_star = threshold_e_star,
  desc_stats       = desc_stats,
  top10_occ        = top10_occ,
  bottom10_occ     = bottom10_occ,
  nobs             = nrow(df),
  n_clusters       = n_clusters_occ,
  seed             = if (exists("PROJECT_SEED", inherits = FALSE)) PROJECT_SEED else 20260413L
)

saveRDS(results, file = file.path(out_dir, "results.rds"), compress = "gzip")
message("Saved analysis results to ", file.path(out_dir, "results.rds"))

# Update data/output/econometrics.json
econometrics_out <- list(
  specifications = list(
    S1  = list(description = "Regressão de exposição sobre escolaridade com controles mincerianos (individual-level)",
               results_clustered_occupation = extract_feols(fit_s1, n_clusters_occ)),
    S2  = list(description = "Regressão de exposição sobre escolaridade, renda e mincerianos",
               results_clustered_occupation = extract_feols(fit_s2, n_clusters_occ)),
    S3a = list(description = "Regressão da taxa de informalidade sobre exposição e mincerianos (incondicional escolaridade)",
               results_clustered_occupation = extract_feols(fit_s3a, n_clusters_occ)),
    S3  = list(description = "Regressão da taxa de informalidade sobre exposição, escolaridade e mincerianos",
               results_clustered_occupation = extract_feols(fit_s3, n_clusters_occ)),
    S4  = list(description = "Gradiente interagido com formalidade regional 27-UF leave-one-out",
               results_clustered_occupation = extract_feols(fit_s4, uniqueN(df_s4$occupation)))
  ),
  disclaimers = list(
    "A unidade de análise é o indivíduo com controles mincerianos (idade, sexo, raça), rodado nos microdados completos.",
    "β1 mede sorting com variância individual, controlando para fatores demográficos estruturais do mercado de trabalho brasileiro.",
    "Erros-padrão são agrupados por ocupação.",
    "Em S4 a formalidade regional varia entre as 27 Unidades da Federação (UFs), resolvendo a fragilidade estatística da estimação original em 5 regiões."
  )
)

econ_json_path <- if (file.exists(file.path(root_dir, "replication_package", "data", "analysis", "econometrics.json"))) {
  file.path(root_dir, "replication_package", "data", "analysis", "econometrics.json")
} else if (file.exists(file.path(root_dir, "data", "analysis", "econometrics.json"))) {
  file.path(root_dir, "data", "analysis", "econometrics.json")
} else {
  file.path(root_dir, "data", "output", "econometrics.json")
}
dir.create(dirname(econ_json_path), showWarnings = FALSE, recursive = TRUE)

jsonlite::write_json(
  econometrics_out,
  path = econ_json_path,
  auto_unbox = TRUE,
  pretty = TRUE
)
message("Updated ", econ_json_path)
