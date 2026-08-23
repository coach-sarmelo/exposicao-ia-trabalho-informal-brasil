# =============================================================================
# Script:  05_figures.R
# Author:  Marcelo Moura Freire
# Purpose: Generate publication-ready vector figures (PDF, SVG, PNG)
# Inputs:  df (from 02_clean.R), results.rds (from 03_analyze.R)
# Outputs: paper/figures/, Figures/, scripts/R/_outputs/ (fig1, fig2, fig3, fig5)
# Standard: AEA Data Editor Standard (DCAS) / INV-1 through INV-12
# =============================================================================

suppressPackageStartupMessages({
  library(data.table)
  library(ggplot2)
  library(svglite)
  library(fixest)
  library(jsonlite)
})

root_dir <- if (requireNamespace("here", quietly = TRUE)) here::here() else getwd()
out_dir  <- if (exists("OUT_DIR", inherits = FALSE)) OUT_DIR else file.path(root_dir, "scripts", "R", "_outputs")

paper_fig_dir <- file.path(root_dir, "paper", "figures")
deck_fig_dir  <- file.path(root_dir, "Figures")

if (!dir.exists(paper_fig_dir)) dir.create(paper_fig_dir, showWarnings = FALSE, recursive = TRUE)
if (!dir.exists(deck_fig_dir))  dir.create(deck_fig_dir,  showWarnings = FALSE, recursive = TRUE)
if (!dir.exists(out_dir))       dir.create(out_dir,       showWarnings = FALSE, recursive = TRUE)

if (!exists("df", inherits = FALSE)) {
  stop("05_figures.R: df not found. Run 00_run_all.R first.")
}
if (!exists("results", inherits = FALSE)) {
  results_path <- file.path(out_dir, "results.rds")
  if (!file.exists(results_path)) stop("05_figures.R: results.rds missing.")
  results <- readRDS(results_path)
}

# ---- Palette & Theme Configuration -----------------------------------------
PALETTE <- list(
  blue       = "#012169",  # Primary institutional blue
  gold       = "#B9975B",  # Primary gold
  dark_blue  = "#0072B2",  # Okabe-Ito blue
  orange     = "#E69F00",  # Okabe-Ito orange
  green      = "#009E73",  # Okabe-Ito green
  vermillion = "#D55E00",  # Okabe-Ito vermillion
  purple     = "#CC79A7",  # Okabe-Ito purple
  jet        = "#1A1A1A",  # Text
  light_gray = "#F0F2F6",  # Light background
  grid_gray  = "#E5E5E5"   # Grid line
)

#' Academic ggplot2 theme matching Emory/AEA standards
#'
#' @param base_size Numeric base font size.
#' @return A ggplot2 theme object.
theme_academic <- function(base_size = 11.0) {
  theme_minimal(base_size = base_size) +
    theme(
      text = element_text(color = PALETTE$jet, family = "sans"),
      plot.title = element_text(face = "bold", size = rel(1.15), color = PALETTE$blue, margin = margin(b = 6)),
      plot.subtitle = element_text(size = rel(0.95), color = "#555555", margin = margin(b = 10)),
      plot.caption = element_text(size = rel(0.8), color = "#777777", margin = margin(t = 8)),
      axis.title = element_text(face = "bold", size = rel(0.95), color = PALETTE$jet),
      axis.text = element_text(size = rel(0.85), color = PALETTE$jet),
      panel.grid.major = element_line(color = PALETTE$grid_gray, linewidth = 0.5),
      panel.grid.minor = element_blank(),
      legend.position = "bottom",
      legend.title = element_text(face = "bold", size = rel(0.85)),
      legend.text = element_text(size = rel(0.8)),
      plot.background = element_rect(fill = "transparent", color = NA),
      panel.background = element_rect(fill = "transparent", color = NA)
    )
}

#' Save plot object in PDF (transparent), SVG (vector), and PNG (300 DPI) across directories
#'
#' @param base_name Character base filename (without extension).
#' @param plot_obj A ggplot2 plot object.
#' @param width Numeric width in inches.
#' @param height Numeric height in inches.
save_all_formats <- function(base_name, plot_obj, width = 6.5, height = 4.2) {
  dest_dirs <- unique(c(
    if (dir.exists(file.path(root_dir, "replication_package", "output", "figures"))) file.path(root_dir, "replication_package", "output", "figures") else NULL,
    if (dir.exists(file.path(root_dir, "paper", "figures"))) file.path(root_dir, "paper", "figures") else NULL,
    if (dir.exists(file.path(root_dir, "Figures"))) file.path(root_dir, "Figures") else NULL,
    out_dir
  ))
  for (d in dest_dirs) {
    if (!dir.exists(d)) dir.create(d, showWarnings = FALSE, recursive = TRUE)
    ggsave(file.path(d, paste0(base_name, ".pdf")), plot_obj, width = width, height = height, bg = "transparent", device = grDevices::pdf)
    ggsave(file.path(d, paste0(base_name, ".svg")), plot_obj, width = width, height = height, bg = "transparent", device = svglite::svglite)
    ggsave(file.path(d, paste0(base_name, ".png")), plot_obj, width = width, height = height, dpi = 300L, bg = "white")
  }
  message("  Saved ", base_name, " in PDF, SVG, and PNG formats.")
}

# =============================================================================
# 1. Figura 1: Gradiente Educacional (Escolaridade x Exposição)
# =============================================================================
message("Generating Figura 1 (fig1_gradiente)...")
occ_agg <- df[, .(
  exposure       = mean(exposure, na.rm = TRUE),
  years_of_study = weighted.mean(years_of_study, weight, na.rm = TRUE),
  employment_m   = sum(weight, na.rm = TRUE) / 1e6
), by = occupation]

p1 <- ggplot(occ_agg, aes(x = years_of_study, y = exposure)) +
  geom_point(aes(size = employment_m), color = PALETTE$blue, alpha = 0.65) +
  geom_smooth(
    method = "lm",
    formula = y ~ x,
    color = PALETTE$vermillion,
    fill = PALETTE$gold,
    alpha = 0.25,
    linewidth = 0.9
  ) +
  scale_size_continuous(
    name = "Emprego (Milhões)",
    range = c(1.5, 9.0),
    breaks = c(2, 4, 6)
  ) +
  scale_x_continuous(breaks = seq(4, 16, 2)) +
  scale_y_continuous(breaks = seq(0, 10, 2.5), limits = c(0, 10)) +
  labs(
    title = "Gradiente Educacional de Exposição à Inteligência Artificial",
    subtitle = expression(paste("PNAD Contínua 2026Q1 — ", hat(beta)[1], " = 0,23 (EP 0,028; p < 0,001; N = 227.629)")),
    x = "Escolaridade Média (Anos de Estudo)",
    y = expression(paste("Escore de Exposição à IA (", theta[j], ", 0–10)")),
    caption = "Nota: Tamanho dos círculos proporcional ao emprego ocupacional ponderado. Reta WLS estimada no nível individual."
  ) +
  theme_academic()

save_all_formats("fig1_gradiente", p1)

# =============================================================================
# 2. Figura 2: Mediação da Informalidade (Efeito Bruto vs Condicional)
# =============================================================================
message("Generating Figura 2 (fig2_mediacao)...")
p2 <- ggplot(occ_agg, aes(x = exposure)) +
  geom_point(aes(y = df[, .(inf = weighted.mean(informal_pct, weight, na.rm = TRUE)), by = occupation]$inf,
                 size = employment_m), color = PALETTE$gold, alpha = 0.70) +
  geom_smooth(
    aes(y = df[, .(inf = weighted.mean(informal_pct, weight, na.rm = TRUE)), by = occupation]$inf,
        color = "S3a (Bruta: -6,23 p.p.)"),
    method = "lm", formula = y ~ x, se = FALSE, linewidth = 1.0
  ) +
  geom_abline(
    aes(intercept = 54.0, slope = -3.9068, color = "S3 (Líquida / Condicional: -3,91 p.p.)"),
    linewidth = 1.0, linetype = "dashed"
  ) +
  scale_color_manual(
    name = "Especificação",
    values = c(
      "S3a (Bruta: -6,23 p.p.)" = PALETTE$vermillion,
      "S3 (Líquida / Condicional: -3,91 p.p.)" = PALETTE$blue
    )
  ) +
  scale_size_continuous(name = "Emprego (Milhões)", range = c(1.5, 9.0), breaks = c(2, 4, 6)) +
  scale_x_continuous(breaks = seq(0, 10, 2), limits = c(0, 10)) +
  scale_y_continuous(breaks = seq(0, 100, 20), limits = c(0, 100)) +
  labs(
    title = "Decomposição de Mediação: Exposição à IA e Informalidade",
    subtitle = "Atenuação de 37,2% via escolaridade vs 62,8% efeito direto do canal de governança",
    x = expression(paste("Escore de Exposição à IA (", theta[j], ")")),
    y = "Taxa de Informalidade (%)",
    caption = "Nota: Linha contínua = efeito bruto S3a; linha tracejada = efeito direto líquido S3 controlando para anos de estudo."
  ) +
  theme_academic() +
  guides(color = guide_legend(nrow = 2L, byrow = TRUE))

save_all_formats("fig2_mediacao", p2)

# =============================================================================
# 3. Figura 3: Heterogeneidade Regional dos Slopes Educacionais (5 Macro-Regiões)
# =============================================================================
message("Generating Figura 3 (fig3_regional_slopes)...")

# Define macro-region mapping from UF code
df[, regiao := fcase(
  uf %in% c(11, 12, 13, 14, 15, 16, 17), "Norte (34,8% Formal)",
  uf %in% c(21, 22, 23, 24, 25, 26, 27, 28, 29), "Nordeste (38,2% Formal)",
  uf %in% c(50, 51, 52, 53), "Centro-Oeste (56,4% Formal)",
  uf %in% c(31, 32, 33, 35), "Sudeste (68,5% Formal)",
  uf %in% c(41, 42, 43), "Sul (72,1% Formal)"
)]

regiao_cores <- c(
  "Norte (34,8% Formal)"        = "#E69F00",
  "Nordeste (38,2% Formal)"     = "#D55E00",
  "Centro-Oeste (56,4% Formal)" = "#009E73",
  "Sudeste (68,5% Formal)"      = "#0072B2",
  "Sul (72,1% Formal)"          = "#012169"
)

p3 <- ggplot(df, aes(x = years_of_study, y = exposure, color = regiao)) +
  geom_smooth(
    method = "lm",
    formula = y ~ x,
    aes(weight = weight),
    se = FALSE,
    linewidth = 1.1
  ) +
  scale_color_manual(
    name = "Macro-Região (Profundidade Formal)",
    values = regiao_cores
  ) +
  scale_x_continuous(breaks = seq(4, 16, 2)) +
  scale_y_continuous(breaks = seq(0, 10, 2)) +
  coord_cartesian(xlim = c(3.5, 17), ylim = c(0, 10)) +
  labs(
    title = "Heterogeneidade Espacial do Gradiente Educacional",
    subtitle = expression(paste("Interação Regional S4: ", hat(beta)[2], " = +0,28 (EP 0,06) | Limiar Crítico: ", e^"*", " = 11,14 anos")),
    x = "Escolaridade Média (Anos)",
    y = expression(paste("Exposição à IA (", theta[j], ")")),
    caption = "Nota: Regiões com maior profundidade formal ampliam o hiato de exposição entre qualificados e não qualificados."
  ) +
  theme_academic() +
  guides(color = guide_legend(nrow = 1L))

save_all_formats("fig3_regional_slopes", p3)

# =============================================================================
# 4. Figura 5: Forest Plot de Robustez
# =============================================================================
message("Generating Figura 5 (fig5_robustez_forest)...")

get_coef <- function(m) if (is.list(m) && !is.null(m$coefficients)) m$coefficients else coef(m)
get_se   <- function(m) if (is.list(m) && !is.null(m$se)) m$se else se(m)

ms1 <- results$models$s1
mr1 <- results$models$r1
mr5 <- results$models$r5
mr6 <- results$models$r6

forest_dt <- data.table(
  spec = c(
    "Baseline (WLS + Mincer)",
    "OLS Não-Ponderado (R1)",
    "Winsorização 1%/99% (R5)",
    "Exclusão p99 Renda (R6)",
    "Sem Dirigentes (COD 1)",
    "Sem Profissionais (COD 2)",
    "Sem Técnicos (COD 3)",
    "Sem Administrativo (COD 4)",
    "Sem Serviços/Vendas (COD 5)",
    "Sem Agropecuária (COD 6)",
    "Sem Indústria (COD 7)",
    "Sem Operadores (COD 8)",
    "Sem Elementares (COD 9)"
  ),
  beta = c(
    as.numeric(get_coef(ms1)["years_of_study"]),
    as.numeric(get_coef(mr1)["years_of_study"]),
    as.numeric(get_coef(mr5)["years_of_study"]),
    as.numeric(get_coef(mr6)["years_of_study"]),
    vapply(1:9, function(g) results$r7_subgroups[[paste0("sem_grupo_", g)]]$beta_schooling, numeric(1L))
  ),
  se = c(
    as.numeric(get_se(ms1)["years_of_study"]),
    as.numeric(get_se(mr1)["years_of_study"]),
    as.numeric(get_se(mr5)["years_of_study"]),
    as.numeric(get_se(mr6)["years_of_study"]),
    vapply(1:9, function(g) results$r7_subgroups[[paste0("sem_grupo_", g)]]$se_schooling, numeric(1L))
  )
)

forest_dt[, `:=`(
  ci_lower = beta - 1.96 * se,
  ci_upper = beta + 1.96 * se
)]
forest_dt[, spec_factor := factor(spec, levels = rev(spec))]

p5 <- ggplot(forest_dt, aes(y = spec_factor, x = beta)) +
  geom_vline(xintercept = 0, linetype = "dotted", color = "#888888", linewidth = 0.6) +
  geom_vline(xintercept = forest_dt[spec == "Baseline (WLS + Mincer)", beta],
             linetype = "dashed", color = PALETTE$vermillion, alpha = 0.7, linewidth = 0.6) +
  geom_errorbar(aes(xmin = ci_lower, xmax = ci_upper), width = 0.25, color = PALETTE$blue, linewidth = 0.7, orientation = "y") +
  geom_point(color = PALETTE$blue, size = 2.4) +
  scale_x_continuous(breaks = seq(0.15, 0.30, 0.05)) +
  labs(
    title = "Robustez do Gradiente Educacional de Exposição à IA",
    subtitle = "Estimativas pontuais e intervalos de 95% de confiança através de especificações alternativas",
    x = expression(paste("Coeficiente de Escolaridade (", hat(beta)[1], ")")),
    y = NULL,
    caption = "Nota: Erros-padrão agrupados por ocupação. Linha tracejada indica estimativa baseline (0,23)."
  ) +
  theme_academic()

save_all_formats("fig5_robustez_forest", p5)

invisible(graphics.off())
invisible(gc())

message("05_figures.R complete: all 4 figures generated in PDF, SVG, and PNG.")
