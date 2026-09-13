# =============================================================================
# Script:  02_clean.R
# Author:  Marcelo Moura Freire
# Purpose: Clean microdata, construct Mincerian controls & LOO regional formality
# Inputs:  raw_microdata, scores_json (from 01_load.R)
# Outputs: df (authoritative analytical data.table)
# Standard: AEA Data Editor Standard (DCAS) / INV-1 through INV-12
# =============================================================================

if (!exists("raw_microdata", inherits = FALSE)) {
  stop("02_clean.R: raw_microdata not found. Run 00_run_all.R first.")
}

suppressPackageStartupMessages({
  library(data.table)
})

df <- data.table::as.data.table(raw_microdata)

# ---- 1. Map Occupational Exposure Score theta_j -----------------------------
scores_map <- unlist(lapply(names(scores_json), function(k) {
  if (k != "_meta" && !is.null(scores_json[[k]]$exposure)) {
    val <- scores_json[[k]]$exposure
    names(val) <- k
    return(val)
  }
  return(NULL)
}))

df[, occupation := as.character(occupation)]
df[, exposure := scores_map[occupation]]

# Filter complete cases on all required econometric dimensions
req_cols <- c("exposure", "years_of_study", "income", "informal", "uf",
              "occupation", "weight", "age", "sex", "race")
df <- df[complete.cases(df[, ..req_cols])]

# ---- 2. Mincerian Covariates ------------------------------------------------
df[, age := as.numeric(age)]
df[, age_sq := age^2]
df[, is_female := as.numeric(sex == 2L)]
df[, race := factor(race)]
df[, income_thousands := as.numeric(income) / 1000.0]
df[, informal_pct := as.numeric(informal) * 100.0]

# ---- 3. Leave-One-Out Regional Formality by UF ------------------------------
df[, formal_weight := weight * (1.0 - informal)]
uf_agg <- df[, .(
  tot_weight = sum(weight, na.rm = TRUE),
  tot_formal = sum(formal_weight, na.rm = TRUE)
), by = uf]

df <- merge(df, uf_agg, by = "uf", all.x = TRUE)
df[, tot_loo := tot_weight - weight]
df[, form_loo := tot_formal - formal_weight]
df[, formality_loo := ifelse(tot_loo > 0, form_loo / tot_loo, NA_real_)]
df[, years_x_formality := years_of_study * formality_loo]

# Clean up temporary helper columns
df[, c("formal_weight", "tot_weight", "tot_formal", "tot_loo", "form_loo") := NULL]

message(sprintf(
  "02_clean.R complete: %d complete cases across %d occupation clusters in `df`.",
  nrow(df), uniqueN(df$occupation)
))
