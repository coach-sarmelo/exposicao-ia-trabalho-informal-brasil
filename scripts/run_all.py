#!/usr/bin/env python3
"""run_all.py — executa a pipeline do projeto sem depender de make.

Uso:
  python scripts/run_all.py             # pipeline completa (equivale a `make refresh`)
  python scripts/run_all.py pipeline
  python scripts/run_all.py paper       # subset do artigo: regenera os artefatos
                                        # usados pelo paper (2026Q1 + econometria),
                                        # sem a série histórica de ~45 trimestres
  python scripts/run_all.py test        # pytest (equivale a `make test`)

Roda tanto no repositório upstream (scripts em <repo>/data/scripts) quanto
dentro do pacote de replicação (scripts em <pkg>/scripts, dados em <pkg>/data):
a resolução é automática via _paths.py e pode ser forçada com a variável de
ambiente PNAD_DATA_ROOT (repassada a todos os subprocessos).

Todos os passos rodam com o mesmo interpretador que invocou este script
(sys.executable). Instale as dependências nele primeiro — veja `make setup`
ou, sem make:  python3 -m pip install -r requirements.txt -r requirements-dev.txt

A ordem dos passos espelha o alvo `refresh` do Makefile (não reordenar):
cada etapa consome o artefato da anterior até as tabelas do artigo em
data/output/. O site (site/) é estático e já vem commitado: não é compilado
por esta pipeline (ver README, seção "Site").
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
from _paths import resolve_data_dir

DATA_DIR = resolve_data_dir()
REPO_ROOT = os.path.dirname(DATA_DIR)
# Repassa a resolução (auto-detecção ou PNAD_DATA_ROOT do usuário) aos
# subprocessos, para que todos os passos concordem sobre o DATA_DIR.
os.environ.setdefault("PNAD_DATA_ROOT", DATA_DIR)

PIPELINE = [
    "fetch_pnad_layout.py",
    "fetch_ibge_microdata.py",
    "process_microdata.py",
    "fetch_historical_microdata.py",
    "build_cod_to_soc_crosswalk.py",
    "compute_ai_exposure.py",
    "compute_decomposition.py",
    "compute_coverage.py",
    "compute_statistics.py",
    "build_regional_panel.py",
    "compute_econometrics.py",
    "stats/logit.py",
    "build_paper_tables.py",
]

# Subset que regenera apenas os artefatos usados pelo artigo: o trimestre
# corrente (2026Q1) em vez da série histórica completa, e inclui
# compute_robustness.py — que produz robustness.json (Tabela 6, R1–R7) mesmo
# não fazendo parte do `refresh` upstream.
PAPER_PIPELINE = [
    "fetch_pnad_layout.py",
    "fetch_ibge_microdata.py",
    "process_microdata.py",
    "build_cod_to_soc_crosswalk.py",
    "compute_ai_exposure.py",
    "compute_decomposition.py",
    "compute_coverage.py",
    "compute_statistics.py",
    "build_regional_panel.py",
    "compute_econometrics.py",
    "stats/logit.py",
    "compute_robustness.py",
    "build_paper_tables.py",
]


def run(args, step=None, cwd=SCRIPTS_DIR):
    label = f"[{step}] " if step else ""
    print(f"{label}>>> {' '.join(args)}", flush=True)
    return subprocess.run(args, cwd=cwd, check=True)


def run_pipeline(steps):
    os.makedirs(os.path.join(DATA_DIR, "output"), exist_ok=True)
    total = len(steps)
    for i, script in enumerate(steps, 1):
        print(f"--- passo {i}/{total}: {script}", flush=True)
        run([sys.executable, os.path.join(SCRIPTS_DIR, script)], step=f"{i}/{total}", cwd=SCRIPTS_DIR)
    print(f"pipeline concluída: {os.path.join(DATA_DIR, 'output')} atualizado.")


def pipeline():
    run_pipeline(PIPELINE)


def paper():
    run_pipeline(PAPER_PIPELINE)


def test():
    if not os.path.isdir(os.path.join(REPO_ROOT, "tests")):
        print("Sem diretório tests/ neste layout (pacote de replicação não distribui os "
              "testes upstream) — nada a executar.")
        return
    run([sys.executable, "-m", "pytest", "-q"], step="test", cwd=REPO_ROOT)


def main():
    ap = argparse.ArgumentParser(
        description="Executa a pipeline do Mapa do Trabalho Brasileiro sem make.")
    ap.add_argument("task", nargs="?", default="pipeline",
                    choices=["pipeline", "paper", "test"])
    args = ap.parse_args()
    if args.task == "pipeline":
        pipeline()
    elif args.task == "paper":
        paper()
    else:
        test()


if __name__ == "__main__":
    main()
