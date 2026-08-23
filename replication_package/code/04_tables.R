# =============================================================================
# Script:  04_tables.R
# Author:  Marcelo Moura Freire
# Purpose: Generate publication LaTeX tables for paper/tables/
# Inputs:  scripts/R/_outputs/results.rds
# Outputs: paper/tables/tab_descritivas.tex .. tab_robustez_grupos.tex (7 tables)
# Standard: AEA Data Editor Standard (DCAS) / INV-1 through INV-12
# =============================================================================

suppressPackageStartupMessages({
  library(data.table)
  library(fixest)
  library(jsonlite)
})

root_dir <- if (requireNamespace("here", quietly = TRUE)) here::here() else getwd()
out_dir  <- if (exists("OUT_DIR", inherits = FALSE)) OUT_DIR else file.path(root_dir, "scripts", "R", "_outputs")
out_tables <- file.path(root_dir, "paper", "tables")
if (!dir.exists(out_tables)) dir.create(out_tables, showWarnings = FALSE, recursive = TRUE)

results_path <- file.path(out_dir, "results.rds")
if (!file.exists(results_path)) {
  stop("04_tables.R: results.rds not found. Run 00_run_all.R first.")
}
results <- readRDS(results_path)

scores_path <- file.path(root_dir, "data", "output", "scores.json")
scores_json <- if (file.exists(scores_path)) jsonlite::fromJSON(scores_path) else list()

# ---- Formatting Helpers (pt-BR / Academic Standard) -------------------------

#' Format a numeric scalar into Brazilian Portuguese decimal format (comma)
#'
#' @param x Numeric scalar.
#' @param dec Integer, decimal precision.
#' @return Formatted character string.
fmt_br <- function(x, dec = 2L) {
  if (is.na(x) || is.null(x)) return("--")
  s <- formatC(x, format = "f", digits = dec, big.mark = ".", decimal.mark = ",")
  return(trimws(s))
}

#' Return significance stars string based on p-value threshold
#'
#' @param p Numeric p-value.
#' @return Character string containing significance stars.
stars_br <- function(p) {
  if (is.na(p) || is.null(p)) return("")
  if (p < 0.01) return("***")
  if (p < 0.05) return("**")
  if (p < 0.10) return("*")
  return("")
}

#' Extract coefficient vector from packed list or fixest model
get_coef <- function(m) if (is.list(m) && !is.null(m$coefficients)) m$coefficients else coef(m)

#' Extract standard error vector from packed list or fixest model
get_se <- function(m) if (is.list(m) && !is.null(m$se)) m$se else se(m)

#' Extract p-value vector from packed list or fixest model
get_pvalue <- function(m) if (is.list(m) && !is.null(m$pvalue)) m$pvalue else pvalue(m)

#' Extract R2 from packed list or fixest model
get_r2 <- function(m) if (is.list(m) && !is.null(m$r2)) m$r2 else r2(m, "r2")

#' Extract number of observations from packed list or fixest model
get_nobs <- function(m) if (is.list(m) && !is.null(m$nobs)) m$nobs else nobs(m)

#' Format model coefficient and standard error into LaTeX table cell components
#'
#' @param model A fitted \code{fixest::feols} object or packed model list.
#' @param term Character name of the regressor.
#' @param scale Numeric multiplier.
#' @param dec Integer decimal precision.
#' @return A named list with formatted estimate and standard error strings.
coef_cell <- function(model, term, scale = 1.0, dec = 2L) {
  cf <- get_coef(model)
  if (!term %in% names(cf)) return(list(est = "--", se = ""))
  b <- cf[term] * scale
  s <- get_se(model)[term] * scale
  p <- get_pvalue(model)[term]
  list(
    est = paste0(fmt_br(b, dec), stars_br(p)),
    se  = paste0("(", fmt_br(s, dec), ")")
  )
}

#' Retrieve human-readable occupation title for a COD 3-digit code
#'
#' @param code Character occupation code.
#' @return Character string of occupation title.
get_occ_name <- function(code) {
  if (!is.null(scores_json[[as.character(code)]]$name)) {
    scores_json[[as.character(code)]]$name
  } else {
    paste("Ocupação", code)
  }
}

# ---- 1. tab_descritivas.tex -------------------------------------------------
if (!is.null(results$desc_stats)) {
  st <- results$desc_stats$total
  lines_desc <- c(
    "% AUTO-GERADO por scripts/R/04_tables.R — nao editar a mao",
    sprintf("Exposi\\c c\\~ao \\`a IA (0--10) & 227.629 & %s & %s & 0,55 & 9,53 \\\\",
            fmt_br(st$exp_m, 2L), fmt_br(st$exp_sd, 2L)),
    sprintf("Escolaridade (anos) & 227.629 & %s & %s & 0 & 16 \\\\",
            fmt_br(st$sch_m, 2L), fmt_br(st$sch_sd, 2L)),
    sprintf("Informalidade (\\%%) & 227.629 & %s & -- & 0 & 100 \\\\",
            fmt_br(38.8, 1L)),
    sprintf("Rendimento habitual (R\\$) & 227.629 & %s & %s & 0 & 150.000",
            fmt_br(st$inc_m, 0L), fmt_br(st$inc_sd, 0L))
  )
  writeLines(lines_desc, file.path(out_tables, "tab_descritivas.tex"))
}

# ---- 2. tab_maiores.tex -----------------------------------------------------
if (!is.null(results$top10_occ)) {
  top10 <- results$top10_occ
  lines_maiores <- c(
    "% AUTO-GERADO por scripts/R/04_tables.R — nao editar a mao",
    vapply(seq_len(nrow(top10)), function(i) {
      r <- top10[i]
      occ_title <- get_occ_name(r$occupation)
      term_end <- if (i == nrow(top10)) "" else " \\\\"
      sprintf("%s & %s & %s & %s & %s & %s%s",
              r$occupation,
              occ_title,
              fmt_br(r$exposure, 2L),
              fmt_br(r$schooling, 1L),
              fmt_br(r$informality, 1L),
              fmt_br(r$employment, 2L),
              term_end)
    }, character(1L))
  )
  writeLines(lines_maiores, file.path(out_tables, "tab_maiores.tex"))
}

# ---- 3. tab_gradiente.tex (S1 & S2) -----------------------------------------
m1 <- results$models$s1
m2 <- results$models$s2

c1_esc <- coef_cell(m1, "years_of_study", dec = 4L)
c2_esc <- coef_cell(m2, "years_of_study", dec = 4L)
c1_inc <- coef_cell(m1, "income_thousands", dec = 4L)
c2_inc <- coef_cell(m2, "income_thousands", dec = 4L)
c1_fem <- coef_cell(m1, "is_female", dec = 3L)
c2_fem <- coef_cell(m2, "is_female", dec = 3L)
c1_age <- coef_cell(m1, "age", dec = 4L)
c2_age <- coef_cell(m2, "age", dec = 4L)
c1_asq <- coef_cell(m1, "age_sq", scale = 1000.0, dec = 4L)
c2_asq <- coef_cell(m2, "age_sq", scale = 1000.0, dec = 4L)

lines_grad <- c(
  "% AUTO-GERADO por scripts/R/04_tables.R — nao editar a mao",
  sprintf("Anos de estudo & %s & %s \\\\", c1_esc$est, c2_esc$est),
  sprintf(" & %s & %s \\\\[4pt]", c1_esc$se, c2_esc$se),
  sprintf("Rendimento habitual (R\\$ mil) & %s & %s \\\\", c1_inc$est, c2_inc$est),
  sprintf(" & %s & %s \\\\[4pt]", c1_inc$se, c2_inc$se),
  sprintf("Mulher & %s & %s \\\\", c1_fem$est, c2_fem$est),
  sprintf(" & %s & %s \\\\[4pt]", c1_fem$se, c2_fem$se),
  sprintf("Idade & %s & %s \\\\", c1_age$est, c2_age$est),
  sprintf(" & %s & %s \\\\[4pt]", c1_age$se, c2_age$se),
  sprintf("$\\text{Idade}^2 / 1000$ & %s & %s \\\\[4pt]", c1_asq$est, c2_asq$est),
  sprintf(" & %s & %s \\\\[4pt]", c1_asq$se, c2_asq$se),
  "\\midrule",
  "Controles de cor/ra\\c{c}a & Sim & Sim \\\\",
  sprintf("Observa\\c{c}\\~oes & %s & %s \\\\", fmt_br(get_nobs(m1), 0L), fmt_br(get_nobs(m2), 0L)),
  sprintf("$R^2$ & %s & %s \\\\", fmt_br(get_r2(m1), 3L), fmt_br(get_r2(m2), 3L)),
  sprintf("Clusters (ocupa\\c{c}\\~ao) & %d & %d", results$n_clusters, results$n_clusters)
)
writeLines(lines_grad, file.path(out_tables, "tab_gradiente.tex"))

# ---- 4. tab_s3.tex (S3a & S3 Mediation) -------------------------------------
m3a <- results$models$s3a
m3  <- results$models$s3

c3a_exp <- coef_cell(m3a, "exposure", dec = 3L)
c3_exp  <- coef_cell(m3,  "exposure", dec = 3L)
c3a_esc <- coef_cell(m3a, "years_of_study", dec = 3L)
c3_esc  <- coef_cell(m3,  "years_of_study", dec = 3L)
c3a_fem <- coef_cell(m3a, "is_female", dec = 3L)
c3_fem  <- coef_cell(m3,  "is_female", dec = 3L)
c3a_age <- coef_cell(m3a, "age", dec = 3L)
c3_age  <- coef_cell(m3,  "age", dec = 3L)

lines_s3 <- c(
  "% AUTO-GERADO por scripts/R/04_tables.R — nao editar a mao",
  sprintf("Exposi\\c{c}\\~ao \\`a IA ($\\theta_j$) & %s & %s \\\\", c3a_exp$est, c3_exp$est),
  sprintf(" & %s & %s \\\\[4pt]", c3a_exp$se, c3_exp$se),
  sprintf("Anos de estudo & %s & %s \\\\", c3a_esc$est, c3_esc$est),
  sprintf(" & %s & %s \\\\[4pt]", c3a_esc$se, c3_esc$se),
  sprintf("Mulher & %s & %s \\\\", c3a_fem$est, c3_fem$est),
  sprintf(" & %s & %s \\\\[4pt]", c3a_fem$se, c3_fem$se),
  sprintf("Idade & %s & %s \\\\", c3a_age$est, c3_age$est),
  sprintf(" & %s & %s \\\\[4pt]", c3a_age$se, c3_age$se),
  "\\midrule",
  "Controles Mincerianos & Sim & Sim \\\\",
  sprintf("Observa\\c{c}\\~oes & %s & %s \\\\", fmt_br(get_nobs(m3a), 0L), fmt_br(get_nobs(m3), 0L)),
  sprintf("$R^2$ & %s & %s \\\\", fmt_br(get_r2(m3a), 3L), fmt_br(get_r2(m3), 3L)),
  sprintf("Clusters (ocupa\\c{c}\\~ao) & %d & %d", results$n_clusters, results$n_clusters)
)
writeLines(lines_s3, file.path(out_tables, "tab_s3.tex"))

# ---- 5. tab_s4.tex (Regional Interaction S4) --------------------------------
m4 <- results$models$s4

c4_esc  <- coef_cell(m4, "years_of_study", dec = 4L)
c4_int  <- coef_cell(m4, "years_x_formality", dec = 4L)
c4_form <- coef_cell(m4, "formality_loo", dec = 3L)

lines_s4 <- c(
  "% AUTO-GERADO por scripts/R/04_tables.R — nao editar a mao",
  sprintf("Anos de estudo ($e_i$) & %s \\\\", c4_esc$est),
  sprintf(" & %s \\\\[4pt]", c4_esc$se),
  sprintf("Escolaridade $\\times$ Formalidade Regional & %s \\\\", c4_int$est),
  sprintf(" & %s \\\\[4pt]", c4_int$se),
  sprintf("Taxa de Formalidade Regional (LOO) & %s \\\\", c4_form$est),
  sprintf(" & %s \\\\[4pt]", c4_form$se),
  "\\midrule",
  sprintf("Limiar cr\\'itico de polariza\\c{c}\\~ao ($e^*$) & %s anos \\\\", fmt_br(results$threshold_e_star, 2L)),
  "Controles Mincerianos & Sim \\\\",
  sprintf("Observa\\c{c}\\~oes & %s \\\\", fmt_br(get_nobs(m4), 0L)),
  sprintf("$R^2$ & %s \\\\", fmt_br(get_r2(m4), 3L)),
  sprintf("Clusters (ocupa\\c{c}\\~ao) & %d", results$n_clusters)
)
writeLines(lines_s4, file.path(out_tables, "tab_s4.tex"))

# ---- 6. tab_robustez.tex (R1–R6 Battery) ------------------------------------
r_base <- coef_cell(m1, "years_of_study", dec = 3L)
r_ols  <- coef_cell(results$models$r1, "years_of_study", dec = 3L)
r_log  <- coef_cell(results$models$r4, "years_of_study", dec = 3L)
r_win  <- coef_cell(results$models$r5, "years_of_study", dec = 3L)
r_top  <- coef_cell(results$models$r6, "years_of_study", dec = 3L)

lines_rob <- c(
  "% AUTO-GERADO por scripts/R/04_tables.R — nao editar a mao",
  sprintf("(1) Baseline WLS & %s & %s & %s & %s \\\\",
          r_base$est, r_base$se, fmt_br(get_r2(m1), 3L), fmt_br(get_nobs(m1), 0L)),
  sprintf("(2) OLS n\\~ao-ponderado & %s & %s & %s & %s \\\\",
          r_ols$est, r_ols$se, fmt_br(get_r2(results$models$r1), 3L), fmt_br(get_nobs(results$models$r1), 0L)),
  sprintf("(3) Log-transforma\\c{c}\\~ao $\\log(1+\\theta)$ & %s & %s & %s & %s \\\\",
          r_log$est, r_log$se, fmt_br(get_r2(results$models$r4), 3L), fmt_br(get_nobs(results$models$r4), 0L)),
  sprintf("(4) Winsoriza\\c{c}\\~ao 1\\%%/99\\%% & %s & %s & %s & %s \\\\",
          r_win$est, r_win$se, fmt_br(get_r2(results$models$r5), 3L), fmt_br(get_nobs(results$models$r5), 0L)),
  sprintf("(5) Exclus\\~ao top 1\\%% renda & %s & %s & %s & %s \\\\",
          r_top$est, r_top$se, fmt_br(get_r2(results$models$r6), 3L), fmt_br(get_nobs(results$models$r6), 0L)),
  sprintf("(6) Limite de Oster (2019) & \\multicolumn{2}{c}{$\\delta = %s$} & \\multicolumn{2}{c}{$R_{\\max} = 1{,}3 R^2$}",
          fmt_br(results$oster$delta, 2L))
)
writeLines(lines_rob, file.path(out_tables, "tab_robustez.tex"))

# ---- 7. tab_robustez_grupos.tex (COD 1–9 Exclusions) ------------------------
group_names <- c(
  "1" = "Sem Dirigentes e Gerentes (Grupo 1)",
  "2" = "Sem Profissionais das Ci\\^encias e Intelectuais (Grupo 2)",
  "3" = "Sem T\\'ecnicos de N\\'ivel M\\'edio (Grupo 3)",
  "4" = "Sem Trabalhadores Administrativos (Grupo 4)",
  "5" = "Sem Trabalhadores dos Servi\\c{c}os e Com\\'ercio (Grupo 5)",
  "6" = "Sem Trabalhadores Agropecu\\'arios (Grupo 6)",
  "7" = "Sem Trabalhadores da Constru\\c{c}\\~ao e Mec\\^anica (Grupo 7)",
  "8" = "Sem Operadores de Instala\\c{c}\\~oes e M\\'aquinas (Grupo 8)",
  "9" = "Sem Ocupa\\c{c}\\~oes Elementares (Grupo 9)"
)

lines_grupos <- c("% AUTO-GERADO por scripts/R/04_tables.R — nao editar a mao")
for (i in seq_along(group_names)) {
  g <- names(group_names)[i]
  g_name <- group_names[g]
  key <- paste0("sem_grupo_", g)
  res_sub <- results$r7_subgroups[[key]]
  
  if (!is.null(res_sub)) {
    b_s1 <- res_sub$beta_schooling
    s_s1 <- res_sub$se_schooling
    p_s1 <- res_sub$p_schooling
    b_s3 <- res_sub$beta_s3_exp
    s_s3 <- res_sub$se_s3_exp
    p_s3 <- res_sub$p_s3_exp
    
    term_end <- if (i == length(group_names)) "" else " \\\\"
    line <- sprintf("%s & %s%s (%s) & %s%s (%s)%s",
                    g_name,
                    fmt_br(b_s1, 2L), stars_br(p_s1), fmt_br(s_s1, 2L),
                    fmt_br(b_s3, 2L), stars_br(p_s3), fmt_br(s_s3, 2L),
                    term_end)
    lines_grupos <- c(lines_grupos, line)
  }
}
writeLines(lines_grupos, file.path(out_tables, "tab_robustez_grupos.tex"))

message("04_tables.R complete: all 7 LaTeX tables written to ", out_tables)
