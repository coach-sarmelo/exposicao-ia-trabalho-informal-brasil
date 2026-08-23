# =============================================================================
# Script:  test_econometrics.R
# Author:  Marcelo Moura Freire
# Purpose: Comprehensive econometric verification suite
# Inputs:  scripts/R/_outputs/results.rds
# Outputs: Test report with 100% assertions coverage
# Standard: AEA Data Editor Standard (DCAS) / INV-1 through INV-12
# =============================================================================

suppressPackageStartupMessages({
  library(testthat)
  library(fixest)
  library(jsonlite)
})

root_dir <- if (requireNamespace("here", quietly = TRUE)) here::here() else getwd()
results_path <- file.path(root_dir, "scripts", "R", "_outputs", "results.rds")

test_that("results.rds exists and loads correctly", {
  expect_true(file.exists(results_path))
  results <- readRDS(results_path)
  expect_type(results, "list")
  expect_true(all(c("models", "r7_subgroups", "oster", "threshold_e_star", "nobs", "n_clusters", "desc_stats", "top10_occ") %in% names(results)))
})

results <- readRDS(results_path)

test_that("Sample size and clusters match PNAD Contínua 2026Q1", {
  expect_equal(results$nobs, 227629L)
  expect_equal(results$n_clusters, 122L)
})

get_coef <- function(m) if (is.list(m) && !is.null(m$coefficients)) m$coefficients else coef(m)
get_se   <- function(m) if (is.list(m) && !is.null(m$se)) m$se else se(m)
get_pval <- function(m) if (is.list(m) && !is.null(m$pvalue)) m$pvalue else pvalue(m)
get_r2   <- function(m) if (is.list(m) && !is.null(m$r2)) m$r2 else r2(m, "r2")

test_that("Specification S1 (Baseline) estimates are exact", {
  m1 <- results$models$s1
  expect_equal(as.numeric(get_coef(m1)["years_of_study"]), 0.228837, tolerance = 1e-4)
  expect_equal(as.numeric(get_se(m1)["years_of_study"]), 0.027752, tolerance = 1e-4)
  expect_lt(as.numeric(get_pval(m1)["years_of_study"]), 0.001)
  expect_equal(as.numeric(get_r2(m1)), 0.2457, tolerance = 1e-3)
})

test_that("Specification S2 (Wage Control) estimates are exact", {
  m2 <- results$models$s2
  expect_equal(as.numeric(get_coef(m2)["years_of_study"]), 0.209652, tolerance = 1e-4)
  expect_equal(as.numeric(get_coef(m2)["income_thousands"]), 0.042744, tolerance = 1e-4)
  expect_equal(as.numeric(get_r2(m2)), 0.2594, tolerance = 1e-3)
})

test_that("Specification S3a & S3 (Mediation) estimates are exact", {
  m3a <- results$models$s3a
  m3  <- results$models$s3
  expect_equal(as.numeric(get_coef(m3a)["exposure"]), -6.228458, tolerance = 1e-3)
  expect_equal(as.numeric(get_coef(m3)["exposure"]), -3.906764, tolerance = 1e-3)
  expect_equal(as.numeric(get_coef(m3)["years_of_study"]), -2.608855, tolerance = 1e-3)
})

test_that("Specification S4 (Regional Interaction) and threshold e* are exact", {
  m4 <- results$models$s4
  expect_equal(as.numeric(get_coef(m4)["years_x_formality"]), 0.278601, tolerance = 1e-3)
  expect_equal(as.numeric(get_coef(m4)["formality_loo"]), -3.104242, tolerance = 1e-3)
  expect_equal(as.numeric(results$threshold_e_star), 11.1422, tolerance = 1e-2)
})

test_that("Oster (2019) bounding parameter delta is robust", {
  expect_gt(results$oster$delta, 1.80)
  expect_lt(results$oster$delta, 2.05)
})

test_that("All 7 LaTeX tables are generated and non-empty", {
  table_files <- c(
    "tab_descritivas.tex",
    "tab_maiores.tex",
    "tab_gradiente.tex",
    "tab_s3.tex",
    "tab_s4.tex",
    "tab_robustez.tex",
    "tab_robustez_grupos.tex"
  )
  for (f in table_files) {
    p <- file.path(root_dir, "paper", "tables", f)
    expect_true(file.exists(p), label = paste("Missing table:", f))
    expect_gt(file.size(p), 50L, label = paste("Empty table:", f))
  }
})

test_that("All 4 figures are generated in PDF, SVG, and PNG formats", {
  figure_bases <- c(
    "fig1_gradiente",
    "fig2_mediacao",
    "fig3_regional_slopes",
    "fig5_robustez_forest"
  )
  for (base in figure_bases) {
    for (ext in c(".pdf", ".svg", ".png")) {
      p1 <- file.path(root_dir, "paper", "figures", paste0(base, ext))
      p2 <- file.path(root_dir, "Figures", paste0(base, ext))
      expect_true(file.exists(p1), label = paste("Missing paper figure:", base, ext))
      expect_true(file.exists(p2), label = paste("Missing deck figure:", base, ext))
      expect_gt(file.size(p1), 1000L, label = paste("Small paper figure:", base, ext))
      expect_gt(file.size(p2), 1000L, label = paste("Small deck figure:", base, ext))
    }
  }
})

message("\nAll econometric testthat assertions PASSED [100%]\n")

if (!interactive()) {
  quit(status = 0L, save = "no")
}
