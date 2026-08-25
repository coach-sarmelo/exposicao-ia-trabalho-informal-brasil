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

root_dir <- if (requireNamespace("here", quietly = TRUE)) here::here() else getwd()

# Locate code directory
code_dir <- if (dir.exists(file.path(root_dir, "replication_package", "code"))) {
  file.path(root_dir, "replication_package", "code")
} else if (dir.exists(file.path(root_dir, "code"))) {
  file.path(root_dir, "code")
} else if (dir.exists(file.path(root_dir, "scripts", "R"))) {
  file.path(root_dir, "scripts", "R")
} else {
  getwd()
}

# Locate output directory
OUT_DIR <- if (exists("OUT_DIR", inherits = FALSE) && !is.null(OUT_DIR)) {
  OUT_DIR
} else if (dir.exists(file.path(root_dir, "replication_package", "output"))) {
  file.path(root_dir, "replication_package", "output")
} else if (dir.exists(file.path(root_dir, "output"))) {
  file.path(root_dir, "output")
} else if (dir.exists(file.path(root_dir, "scripts", "R", "_outputs"))) {
  file.path(root_dir, "scripts", "R", "_outputs")
} else {
  file.path(code_dir, "_outputs")
}
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
  path <- file.path(code_dir, script)
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
