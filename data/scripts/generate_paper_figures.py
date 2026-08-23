#!/usr/bin/env python3
"""
generate_paper_figures.py
Gera figuras de qualidade para publicação acadêmica (PDF e PNG) em paper/figures/
usando os dados reais calculados pelo pipeline em data/output/.
Refatorado usando os princípios visuais do matlab-plot-skill (Okabe-Ito, espaçamento, legibilidade).
"""
from __future__ import annotations

import json
import os
import numpy as np
import matplotlib.pyplot as plt

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(SCRIPTS_DIR)
REPO_ROOT = os.path.dirname(DATA_DIR)
OUTPUT_DIR = os.path.join(REPO_ROOT, "paper", "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# Paleta Okabe-Ito (colorblind-safe)
OKABE_ITO = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "purple": "#CC79A7",
    "yellow": "#F0E442",
    "skyblue": "#56B4E9",
    "vermillion": "#D55E00",
    "black": "#000000"
}

# Configuração de estilo Tufte / JEP com fontes Arial para compatibilidade
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 9,
    'figure.titlesize': 13,
    'axes.linewidth': 1.0,
    'axes.edgecolor': '#333333',
    'grid.color': '#E5E5E5',
    'grid.linestyle': '-',
    'grid.linewidth': 0.6,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'pdf.fonttype': 42,
    'ps.fonttype': 42
})

def load_json(filepath):
    if not os.path.isabs(filepath):
        if filepath.startswith("data/output/"):
            filepath = os.path.join(DATA_DIR, "output", os.path.basename(filepath))
        elif filepath.startswith("data/"):
            filepath = os.path.join(REPO_ROOT, filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_fig1_gradient():
    """Figura 1: Dispersão ponderada e gradiente Escolaridade x Exposição."""
    panel = load_json("data/output/regional_panel.json")["data"]
    econ = load_json("data/output/econometrics.json")["specifications"]["S1"]
    res = econ.get("results_clustered_occupation") or econ["results"]
    
    escolaridade = np.array([d["avg_anos_estudo"] for d in panel])
    exposicao = np.array([d["exposure"] for d in panel])
    emprego = np.array([d["jobs"] for d in panel])
    
    b1_ind = res["beta"][1]
    se1_ind = res["se"][1]
    
    w = emprego / emprego.sum()
    W = np.diag(w)
    X = np.column_stack([np.ones_like(escolaridade), escolaridade])
    b_cell = np.linalg.inv(X.T @ W @ X) @ (X.T @ W @ exposicao)
    b0_cell, b1_cell = b_cell[0], b_cell[1]
    
    fig, ax = plt.subplots(figsize=(7.0, 5.2))
    
    sizes = 15 + 200 * (emprego - emprego.min()) / (emprego.max() - emprego.min())
    
    ax.scatter(
        escolaridade, exposicao, s=sizes,
        color=OKABE_ITO["blue"], alpha=0.5, edgecolors="#ffffff", linewidth=0.5, zorder=2,
        label="Célula ocupação × região (área = emprego)"
    )

    x_grid = np.linspace(escolaridade.min(), escolaridade.max(), 100)
    y_fit = b0_cell + b1_cell * x_grid

    ax.plot(x_grid, y_fit, color=OKABE_ITO["vermillion"], linewidth=2.5, zorder=3,
            label=f"Ajuste de célula (WLS): $\\hat{{\\beta}}_1 = {b1_cell:.2f}$")
    
    ci_lo = b1_ind - 1.959964 * se1_ind
    ci_hi = b1_ind + 1.959964 * se1_ind
    ax.text(0.98, 0.04,
            f"Coef. individual (S1): $\\hat{{\\beta}}_1 = {b1_ind:.2f}$ (EP ${se1_ind:.2f}$)\n"
            f"IC 95%: [{ci_lo:.2f}; {ci_hi:.2f}], N = 227.629",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=9,
            color="#333333", bbox=dict(facecolor="white", alpha=0.9, edgecolor="#CCCCCC", boxstyle="round,pad=0.4"),
            zorder=5)

    annotations = [
        ("Construção estrutural\n(θ = 0,9)", 8.3, 0.9, (-30, -45), "right"),
        ("Trabalho doméstico\n(θ = 0,1)", 9.0, 0.1, (25, 20), "left"),
        ("Comerciantes e vendedores\n(θ = 4,1)", 11.7, 4.1, (25, -30), "left"),
        ("Escriturários gerais\n(θ = 5,8)", 13.5, 5.8, (-80, 22), "right"),
        ("Desenvolvedores\n(θ = 7,5)", 15.7, 7.5, (-15, 20), "right"),
    ]

    for text, x_pos, y_pos, offset, ha in annotations:
        ax.annotate(
            text, xy=(x_pos, y_pos), xytext=offset, textcoords="offset points",
            fontsize=9, fontweight="bold", color="#1A1A1A", zorder=4, ha=ha,
            arrowprops=dict(arrowstyle="->", color="#333333", lw=1.2, shrinkB=4,
                            connectionstyle="arc3,rad=0.12")
        )

    ax.set_xlabel("Escolaridade Média da Célula (Anos de Estudo)")
    ax.set_ylabel(r"Índice de Exposição à IA ($\theta_j$)")
    ax.set_xlim(5.0, 17.0)
    ax.set_ylim(-1.5, 10.2)
    ax.grid(True, alpha=0.6, linewidth=0.6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.legend(frameon=True, facecolor="white", edgecolor="#CCCCCC", loc="upper left",
              framealpha=0.95, fontsize=9)
    
    plt.tight_layout()
    pdf_path = os.path.join(OUTPUT_DIR, "fig1_gradiente.pdf")
    png_path = os.path.join(OUTPUT_DIR, "fig1_gradiente.png")
    plt.savefig(pdf_path)
    plt.savefig(png_path)
    plt.close()
    print(f"Gerado: {pdf_path}")


def generate_fig2_mediation():
    """Figura 2: Associação bruta vs. parcial entre Exposição e Informalidade (Mediação)."""
    panel = load_json("data/output/regional_panel.json")["data"]
    econ = load_json("data/output/econometrics.json")["specifications"]
    
    exposicao = np.array([d["exposure"] for d in panel])
    informalidade = np.array([d["informality"] for d in panel])
    escolaridade = np.array([d["avg_anos_estudo"] for d in panel])
    emprego = np.array([d["jobs"] for d in panel])
    
    s3a = econ["S3a"].get("results_clustered_occupation") or econ["S3a"]["results"]
    s3b = econ["S3"].get("results_clustered_occupation") or econ["S3"]["results"]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.0, 4.5))
    
    sizes = 15 + 150 * (emprego - emprego.min()) / (emprego.max() - emprego.min())
    
    # Painel A: Bruta
    ax1.scatter(exposicao, informalidade, s=sizes, color=OKABE_ITO["green"], alpha=0.4, edgecolors="#ffffff", linewidth=0.5)
    w = emprego / emprego.sum()
    W = np.diag(w)
    X_a = np.column_stack([np.ones_like(exposicao), exposicao])
    b_a_cell = np.linalg.inv(X_a.T @ W @ X_a) @ (X_a.T @ W @ informalidade)
    x_grid_a = np.linspace(0.1, 7.8, 100)
    y_fit_a = b_a_cell[0] + b_a_cell[1] * x_grid_a
    lbl_a = f"Ajuste WLS: $\\hat{{\\gamma}}_1 = {b_a_cell[1]:.2f}$ p.p."
    ax1.plot(x_grid_a, y_fit_a, color=OKABE_ITO["vermillion"], linewidth=2.0, label=lbl_a)
    
    ax1.text(0.97, 0.95,
            f"Coef. ind (S3a): $\\hat{{\\gamma}}_1 = {s3a['beta'][1]:.2f}$\n"
            f"(EP ${s3a['se'][1]:.2f}$)***",
            transform=ax1.transAxes, ha="right", va="top", fontsize=8.5,
            color="#333333", bbox=dict(facecolor="white", alpha=0.9, edgecolor="#DDDDDD", boxstyle="round,pad=0.3"))
    
    ax1.set_title(f"A. Relação Bruta (S3a: $R^2 = {s3a['r_squared']:.2f}$)", fontweight="bold", pad=10)
    ax1.set_xlabel(r"Exposição à IA ($\theta_j$)")
    ax1.set_ylabel("Taxa de Informalidade (%)")
    ax1.set_xlim(-0.5, 8.5)
    ax1.set_ylim(-5, 105)
    ax1.grid(True, alpha=0.6)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.legend(frameon=True, facecolor="white", loc="lower left", fontsize=9)
    
    # Painel B: Resíduos parciais
    w = emprego / emprego.sum()
    W = np.diag(w)
    X_e = np.column_stack([np.ones_like(escolaridade), escolaridade])
    
    beta_inf = np.linalg.inv(X_e.T @ W @ X_e) @ (X_e.T @ W @ informalidade)
    res_inf = informalidade - X_e @ beta_inf
    
    beta_exp = np.linalg.inv(X_e.T @ W @ X_e) @ (X_e.T @ W @ exposicao)
    res_exp = exposicao - X_e @ beta_exp
    
    ax2.scatter(res_exp, res_inf, s=sizes, color=OKABE_ITO["skyblue"], alpha=0.4, edgecolors="#ffffff", linewidth=0.5)
    b_partial = np.sum(w * res_exp * res_inf) / np.sum(w * res_exp**2)
    x_grid_b = np.linspace(res_exp.min(), res_exp.max(), 100)
    y_fit_b = b_partial * x_grid_b
    z_b = abs(s3b["beta"][1] / s3b["se"][1])
    stars_b = "***" if z_b > 2.576 else ("**" if z_b > 1.96 else "")
    lbl_b = f"Ajuste WLS: $\\hat{{\\gamma}}_1 = {b_partial:.2f}$ p.p."
    ax2.plot(x_grid_b, y_fit_b, color=OKABE_ITO["vermillion"], linewidth=2.0, linestyle="--", label=lbl_b)
    
    ax2.text(0.97, 0.95,
            f"Coef. ind (S3): $\\hat{{\\gamma}}_1 = {s3b['beta'][1]:.2f}$\n"
            f"(EP ${s3b['se'][1]:.2f}$){stars_b}",
            transform=ax2.transAxes, ha="right", va="top", fontsize=8.5,
            color="#333333", bbox=dict(facecolor="white", alpha=0.9, edgecolor="#DDDDDD", boxstyle="round,pad=0.3"))
    
    ax2.set_title(f"B. Regressão Parcial (S3: $R^2 = {s3b['r_squared']:.2f}$)", fontweight="bold", pad=10)
    ax2.set_xlabel(r"Exposição Residual ($\theta_j \mid \text{escolaridade}$)")
    ax2.set_ylabel(r"Informalidade Residual (% $\mid \text{escolaridade}$)")
    ax2.grid(True, alpha=0.6)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.legend(frameon=True, facecolor="white", loc="lower left", fontsize=9)
    
    plt.tight_layout()
    pdf_path = os.path.join(OUTPUT_DIR, "fig2_mediacao.pdf")
    png_path = os.path.join(OUTPUT_DIR, "fig2_mediacao.png")
    plt.savefig(pdf_path)
    plt.savefig(png_path)
    plt.close()
    print(f"Gerado: {pdf_path}")


def generate_fig3_regional_slopes():
    """Figura 3: Inclinação do gradiente por Grande Região."""
    panel = load_json("data/output/regional_panel.json")["data"]
    
    regioes = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
    cores = {
        "Norte": OKABE_ITO["orange"],
        "Nordeste": OKABE_ITO["vermillion"],
        "Centro-Oeste": OKABE_ITO["green"],
        "Sudeste": OKABE_ITO["blue"],
        "Sul": OKABE_ITO["purple"]
    }
    
    formality_map = {}
    for reg in regioes:
        sub = [d for d in panel if d["region"] == reg]
        total_emp = sum(d["jobs"] for d in sub)
        weighted_inf = sum(d["jobs"] * d["informality"] / total_emp for d in sub)
        formality_map[reg] = (100.0 - weighted_inf) / 100.0
    
    fig, ax = plt.subplots(figsize=(7.5, 5.0))
    
    for reg in regioes:
        sub = [d for d in panel if d["region"] == reg]
        esc = np.array([d["avg_anos_estudo"] for d in sub])
        exp = np.array([d["exposure"] for d in sub])
        emp = np.array([d["jobs"] for d in sub])
        
        ax.scatter(esc, exp, s=20 + 80*(emp/emp.max()), color=cores[reg], alpha=0.35, edgecolors="none")
        
        w = emp / emp.sum()
        X = np.column_stack([np.ones_like(esc), esc])
        b = np.linalg.inv(X.T @ np.diag(w) @ X) @ (X.T @ np.diag(w) @ exp)
        
        x_line = np.linspace(esc.min(), esc.max(), 50)
        lbl = f"{reg} (form.: {formality_map[reg]*100:.0f}%, slope = {b[1]:.2f})"
        ax.plot(x_line, b[0] + b[1]*x_line, color=cores[reg], linewidth=2.0, label=lbl)
    
    ax.set_xlabel("Escolaridade Média da Célula (Anos de Estudo)")
    ax.set_ylabel(r"Índice de Exposição à IA ($\theta_j$)")
    ax.set_title("Heterogeneidade Regional: Gradiente mais íngreme onde a formalidade é profunda", fontweight="bold", pad=12)
    ax.set_xlim(5.0, 16.5)
    ax.set_ylim(-0.5, 9.0)
    ax.grid(True, alpha=0.6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Legenda movida para fora do gráfico para não sobrepor dados
    ax.legend(frameon=True, facecolor="white", edgecolor="#CCCCCC", 
              loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=9)
    
    plt.tight_layout()
    pdf_path = os.path.join(OUTPUT_DIR, "fig3_regional_slopes.pdf")
    png_path = os.path.join(OUTPUT_DIR, "fig3_regional_slopes.png")
    plt.savefig(pdf_path)
    plt.savefig(png_path)
    plt.close()
    print(f"Gerado: {pdf_path}")


def generate_fig5_forest_robustness():
    """Figura 5: Forest plot / coefficient plot de robustez (Tabela A1)."""
    rob = load_json("data/output/robustness.json")
    
    labels = [
        "Linha de Base (Amostra Completa)",
        "Sem Dirigentes e gerentes",
        "Sem Profissionais das ciências",
        "Sem Técnicos de nível médio",
        "Sem Apoio administrativo",
        "Sem Serviços e vendedores",
        "Sem Agropecuária e pesca",
        "Sem Indústria e construção",
        "Sem Operadores e montadores",
        "Sem Ocupações elementares",
        "Sem Ponderação (OLS não-ponderado)",
        "Exposição Winsorizada (1%/99%)",
        "Sem Outliers (exclui p > 99)"
    ]
    
    baseline_b = rob["R1_weighting"]["weighted"]["beta"][1]
    baseline_se = rob["R1_weighting"]["weighted"]["se"][1]
    
    betas = [baseline_b]
    ses = [baseline_se]
    
    # 9 grupos
    for g in range(1, 10):
        b = rob["R3_drop_major_group"]["by_group"][str(g)]["beta"][1]
        se = rob["R3_drop_major_group"]["by_group"][str(g)]["se"][1]
        betas.append(b)
        ses.append(se)
        
    # Unweighted
    betas.append(rob["R1_weighting"]["unweighted"]["beta"][1])
    ses.append(rob["R1_weighting"]["unweighted"]["se"][1])
    
    # Winsorized
    betas.append(rob["R5_outliers"]["winsorized_1_99"]["beta"][1])
    ses.append(rob["R5_outliers"]["winsorized_1_99"]["se"][1])
    
    # Trimming
    betas.append(rob["R5_outliers"]["dropped_above_p99"]["beta"][1])
    ses.append(rob["R5_outliers"]["dropped_above_p99"]["se"][1])
    
    betas = np.array(betas)
    ses = np.array(ses)
    ci_low = betas - 1.96 * ses
    ci_high = betas + 1.96 * ses
    
    M = len(betas)
    y_pos = np.arange(M, 0, -1)
    
    fig, ax = plt.subplots(figsize=(7.5, 5.5))  # Aumentado para respiro
    
    ax.axvline(baseline_b, color="#999999", linestyle="--", linewidth=1.5, zorder=1)
    
    for i in range(M):
        if i == 0:
            col = OKABE_ITO["vermillion"]
            marker = "s"
            ms = 7.0
        elif i >= 10:
            col = OKABE_ITO["green"]
            marker = "D"
            ms = 6.0
        else:
            col = OKABE_ITO["blue"]
            marker = "o"
            ms = 6.0
            
        ax.plot([ci_low[i], ci_high[i]], [y_pos[i], y_pos[i]], color=col, linewidth=1.8, zorder=2)
        ax.plot(betas[i], y_pos[i], marker=marker, markersize=ms, color=col, markeredgecolor="white", zorder=3)
        
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9.5)
    ax.set_xlabel(r"Coeficiente da Escolaridade ($\hat{\beta}_1$) $\pm$ IC 95%", fontsize=11)
    ax.set_title("Estabilidade do Gradiente sob Variações de Amostra e Ponderação", fontweight="bold", pad=12)
    ax.set_xlim(min(ci_low) - 0.05, max(ci_high) + 0.05)
    ax.set_ylim(0.2, M + 0.8)
    ax.grid(True, alpha=0.6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add explicit legend for baseline
    ax.plot([], [], color=OKABE_ITO["vermillion"], marker="s", label=f"Linha de Base ({baseline_b:.2f})", linestyle="none")
    ax.legend(frameon=True, facecolor="white", edgecolor="#CCCCCC", loc="upper right")
    
    plt.tight_layout()
    pdf_path = os.path.join(OUTPUT_DIR, "fig5_robustez_forest.pdf")
    png_path = os.path.join(OUTPUT_DIR, "fig5_robustez_forest.png")
    plt.savefig(pdf_path)
    plt.savefig(png_path)
    plt.close()
    print(f"Gerado: {pdf_path}")


if __name__ == "__main__":
    print("Gerando figuras do artigo...")
    generate_fig1_gradient()
    generate_fig2_mediation()
    generate_fig3_regional_slopes()
    generate_fig5_forest_robustness()
    print("Todas as figuras geradas com sucesso em paper/figures/.")
