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

# ---- 1. Microdata -----------------------------------------------------------
microdata_path <- file.path(root_dir, "data", "output", "individual_microdata.csv")
if (!file.exists(microdata_path)) {
  stop("01_load.R: individual_microdata.csv not found at ", microdata_path)
}
raw_microdata <- data.table::fread(microdata_path)
message("Loaded ", nrow(raw_microdata), " microdata rows from ", microdata_path)

# ---- 2. Reference & Benchmark JSONs -----------------------------------------
scores_path <- file.path(root_dir, "data", "output", "scores.json")
scores_json <- jsonlite::fromJSON(scores_path)

panel_path <- file.path(root_dir, "data", "output", "regional_panel.json")
if (file.exists(panel_path)) {
  regional_panel_json <- jsonlite::fromJSON(panel_path)
} else {
  regional_panel_json <- list()
}

cod_path <- file.path(root_dir, "data", "reference", "cod_estrutura.json")
if (file.exists(cod_path)) {
  cod_estrutura_json <- jsonlite::fromJSON(cod_path)
} else {
  cod_estrutura_json <- list()
}

uf_path <- file.path(root_dir, "data", "reference", "uf_codes.json")
if (file.exists(uf_path)) {
  uf_codes_json <- jsonlite::fromJSON(uf_path)
} else {
  uf_codes_json <- list()
}

message("01_load.R complete: loaded microdata and JSON reference mappings.")
