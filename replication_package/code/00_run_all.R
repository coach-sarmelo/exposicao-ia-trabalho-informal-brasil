# =============================================================================
# Script:  00_run_all.R
# Author:  Marcelo Moura Freire
# Purpose: Master orchestrator. Run complete canonical R reproducibility pipeline.
# Inputs:  scripts/R/01_load.R .. 05_figures.R
# Outputs: scripts/R/_outputs/ (results.rds, sessionInfo.txt, figures)
# Standard: AEA Data Editor Standard (DCAS) / INV-1 through INV-12
# =============================================================================

# ---- Bootstrap -------------------------------------------------------------
suppressPackageStartupMessages({
  if (!requireNamespace("here", quietly = TRUE)) {
    stop("Install 'here' first: install.packages('here')")
  }
  library(here)
})

# Master random seed applied across the pipeline
PROJECT_SEED <- 20260413L
set.seed(PROJECT_SEED)

# Output directory for pipeline artifacts
OUT_DIR <- here("scripts", "R", "_outputs")
dir.create(OUT_DIR, showWarnings = FALSE, recursive = TRUE)

# ---- Pipeline Execution ----------------------------------------------------
pipeline_env <- new.env(parent = globalenv())
pipeline_env$PROJECT_SEED <- PROJECT_SEED
pipeline_env$OUT_DIR      <- OUT_DIR

pipeline <- c(
  "01_load.R",
  "02_clean.R",
  "03_analyze.R",
  "04_tables.R",
  "05_figures.R"
)

message("Running reproducibility pipeline with seed ", PROJECT_SEED, "...")

timings <- vapply(pipeline, function(script) {
  path <- here("scripts", "R", script)
  if (!file.exists(path)) {
    stop("Missing pipeline script: ", path)
  }
  start <- Sys.time()
  source(path, local = pipeline_env)
  elapsed <- as.numeric(Sys.time() - start, units = "secs")
  message(sprintf("  %s -> %.2fs", script, elapsed))
  elapsed
}, numeric(1L))

# ---- Session Capture -------------------------------------------------------
writeLines(
  capture.output(sessionInfo()),
  con = file.path(OUT_DIR, "sessionInfo.txt")
)

# ---- Reporting & Safe Exit -------------------------------------------------
outputs <- list.files(OUT_DIR, full.names = FALSE)
message("")
message("Pipeline complete. Total time: ", sprintf("%.2fs", sum(timings)))
message(paste(c("Outputs in _outputs:", paste0("  - ", outputs)), collapse = "\n"))

if (!interactive()) {
  quit(status = 0L, save = "no")
}
