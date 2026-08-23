# =============================================================================
# Script:  01_load.R
# Author:  Marcelo Moura Freire
# Purpose: Load raw microdata and JSON reference mappings into memory
# Inputs:  data/output/individual_microdata.csv, data/output/scores.json,
#          data/output/regional_panel.json, data/reference/cod_estrutura.json
# Outputs: raw_microdata, scores_json, regional_panel_json, cod_estrutura_json
# Standard: AEA Data Editor Standard (DCAS) / INV-1 through INV-12
# =============================================================================

suppressPackageStartupMessages({
  library(data.table)
  library(jsonlite)
})

# Seed discipline: only set seed if running standalone
if (!exists("PROJECT_SEED", inherits = FALSE)) {
  set.seed(20260413L)
}

root_dir <- if (requireNamespace("here", quietly = TRUE)) here::here() else getwd()

find_path <- function(relative_options) {
  for (opt in relative_options) {
    p <- file.path(root_dir, opt)
    if (file.exists(p)) return(p)
  }
  return(file.path(root_dir, relative_options[1]))
}

# ---- 1. Microdata -----------------------------------------------------------
microdata_path <- find_path(c(
  file.path("replication_package", "data", "analysis", "individual_microdata.csv"),
  file.path("data", "analysis", "individual_microdata.csv"),
  file.path("data", "output", "individual_microdata.csv")
))
if (!file.exists(microdata_path)) {
  stop("01_load.R: individual_microdata.csv not found at ", microdata_path)
}
raw_microdata <- data.table::fread(microdata_path)
message("Loaded ", nrow(raw_microdata), " microdata rows from ", microdata_path)

# ---- 2. Reference & Benchmark JSONs -----------------------------------------
scores_path <- find_path(c(
  file.path("replication_package", "data", "analysis", "scores.json"),
  file.path("data", "analysis", "scores.json"),
  file.path("data", "output", "scores.json")
))
scores_json <- jsonlite::fromJSON(scores_path)

panel_path <- find_path(c(
  file.path("replication_package", "data", "analysis", "regional_panel.json"),
  file.path("data", "analysis", "regional_panel.json"),
  file.path("data", "output", "regional_panel.json")
))
if (file.exists(panel_path)) {
  regional_panel_json <- jsonlite::fromJSON(panel_path)
} else {
  regional_panel_json <- list()
}

cod_path <- find_path(c(
  file.path("replication_package", "data", "reference", "cod_estrutura.json"),
  file.path("data", "reference", "cod_estrutura.json"),
  file.path("data", "scripts", "reference", "cod_estrutura.json")
))
if (file.exists(cod_path)) {
  cod_estrutura_json <- jsonlite::fromJSON(cod_path)
} else {
  cod_estrutura_json <- list()
}

uf_path <- find_path(c(
  file.path("replication_package", "data", "reference", "uf_codes.json"),
  file.path("data", "reference", "uf_codes.json"),
  file.path("data", "scripts", "reference", "uf_codes.json")
))
if (file.exists(uf_path)) {
  uf_codes_json <- jsonlite::fromJSON(uf_path)
} else {
  uf_codes_json <- list()
}

message("01_load.R complete: loaded microdata and JSON reference mappings.")
