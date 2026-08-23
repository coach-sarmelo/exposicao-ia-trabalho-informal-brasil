#!/usr/bin/env python3
"""run_all.py — executa a pipeline do projeto sem depender de make.

Uso:
  python scripts/run_all.py             # pipeline completa (equivale a `make refresh`)
  python scripts/run_all.py pipeline
  python scripts/run_all.py test        # pytest (equivale a `make test`)

Todos os passos rodam com o mesmo interpretador que invocou este script
(sys.executable). Instale as dependências nele primeiro — veja `make setup`
ou, sem make:  python3 -m pip install -r requirements.txt -r requirements-dev.txt

A ordem dos passos espelha o alvo `refresh` do Makefile (não reordenar):
cada etapa consome o artefato da anterior, de data/microdata/ até as tabelas
do artigo em data/output/. O site (site/) é estático e já vem commitado:
não é compilado por esta pipeline (ver README, seção "Site").
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(SCRIPTS_DIR)
REPO_ROOT = os.path.dirname(DATA_DIR)

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


def run(args, step=None, cwd=SCRIPTS_DIR):
    label = f"[{step}] " if step else ""
    print(f"{label}>>> {' '.join(args)}", flush=True)
    return subprocess.run(args, cwd=cwd, check=True)


def pipeline():
    total = len(PIPELINE)
    for i, script in enumerate(PIPELINE, 1):
        print(f"--- passo {i}/{total}: {script}", flush=True)
        run([sys.executable, os.path.join(SCRIPTS_DIR, script)], step=f"{i}/{total}", cwd=SCRIPTS_DIR)
    print("pipeline concluída: data/output/ atualizado.")


def test():
    run([sys.executable, "-m", "pytest", "-q"], step="test", cwd=REPO_ROOT)


def main():
    ap = argparse.ArgumentParser(
        description="Executa a pipeline do Mapa do Trabalho Brasileiro sem make.")
    ap.add_argument("task", nargs="?", default="pipeline",
                    choices=["pipeline", "test"])
    args = ap.parse_args()
    if args.task == "pipeline":
        pipeline()
    else:
        test()


if __name__ == "__main__":
    main()