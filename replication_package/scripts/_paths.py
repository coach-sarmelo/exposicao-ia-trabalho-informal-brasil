"""Resolução compartilhada de caminhos para os scripts da pipeline.

Funciona nos dois layouts suportados, sem configuração:

  * repositório upstream:  <repo>/data/scripts/  →  DATA_DIR = <repo>/data
    (contém external/, microdata/ e output/)
  * pacote de replicação:  <pkg>/scripts/        →  DATA_DIR = <pkg>/data
    (contém analysis/, external/ e reference/; output/ é criado sob demanda)

A variável de ambiente ``PNAD_DATA_ROOT`` tem precedência sobre a
auto-detecção — útil para redirecionar entradas/saídas para fora do pacote
(p. ex. manter o pacote limpo antes do depósito) ou para apontar para um
checkout upstream a partir de qualquer lugar.
"""
from __future__ import annotations

import os

ENV_VAR = "PNAD_DATA_ROOT"


def resolve_data_dir() -> str:
    """Retorna o DATA_DIR efetivo (``external/`` fica direto dentro dele)."""
    override = os.environ.get(ENV_VAR)
    if override:
        return os.path.abspath(override)

    default = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.isdir(os.path.join(default, "external")):
        return default  # layout upstream: <repo>/data
    pkg_data = os.path.join(default, "data")
    if os.path.isdir(os.path.join(pkg_data, "external")):
        return pkg_data  # layout pacote de replicação: <pkg>/data
    return default  # layout desconhecido: mantém o comportamento upstream


def ensure_output_dir(data_dir: str) -> str:
    """Garante que <data_dir>/output/ exista e retorna o caminho."""
    out = os.path.join(data_dir, "output")
    os.makedirs(out, exist_ok=True)
    return out
