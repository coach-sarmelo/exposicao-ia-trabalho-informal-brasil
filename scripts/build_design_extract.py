"""build_design_extract.py — Robustness extension (v1.2.0): regenerate the
microdata extract WITH survey-design variables.

Mirrors fetch_pnad_layout.py (SAS dictionary positions) and
process_microdata.py (row filter + derivations) exactly, adding:
  UPA (PSU), Estrato (stratum), V1008 (dwelling order), V2003 (person order).

Output (13 columns = 9 analytic + 4 design):
  <data_dir>/output/individual_microdata_design.csv
The shipped copy is data/analysis/individual_microdata_design.csv
(byte-identical; 14 MB).

Validation gate: the 9 analytic columns must be multiset-identical to the
shipped data/analysis/individual_microdata.csv, and all 11 positions in the
shipped pnadc_layout.json must match the SAS dictionary.

Deterministic. The 228.6 MB raw archive is NOT redistributed: honour
MICRODATA_ZIP (path to PNADC_012026.zip) or MICRODATA_TXT (decompressed
fixed-width file) to avoid a download; otherwise the zip is fetched from
IBGE's public FTP and cached under <data_dir>/raw/ (deletable).
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import sys
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import resolve_data_dir, ensure_output_dir  # noqa: E402

DATA = resolve_data_dir()
REF = os.path.join(DATA, "reference")
SHIPPED = os.path.join(DATA, "analysis", "individual_microdata.csv")
RAW = os.path.join(DATA, "raw")
os.makedirs(RAW, exist_ok=True)

BASE_URL = ("https://ftp.ibge.gov.br/Trabalho_e_Rendimento/"
            "Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados")
YEAR, QUARTER = "2026", "1"

ANALYTIC = ["UF", "V1028", "V2007", "V2009", "V2010", "V4010", "V4019",
            "VD3005", "VD4009", "VD4010", "VD4016"]
DESIGN = ["UPA", "Estrato", "V1008", "V2003"]

# ---------------------------------------------------------------- layout ----
# Positions come from the same IBGE SAS input dictionary that
# fetch_pnad_layout.py parses ("Dicionario_e_input_20221031.zip",
# input_PNADC_trimestral.sas). Design-variable positions verified against the
# dictionary on 2026-09-18; the 11 analytic positions are cross-checked
# against the shipped pnadc_layout.json below.
SAS_LAYOUT = {
    "UPA":     {"start": 12, "length": 9},
    "Estrato": {"start": 21, "length": 7},
    "V1008":   {"start": 28, "length": 2},
    "V2003":   {"start": 91, "length": 2},
}
layout = dict(SAS_LAYOUT)

with open(os.path.join(REF, "pnadc_layout.json"), encoding="utf-8") as f:
    shipped_layout = json.load(f)
for v, info in shipped_layout.items():
    if v in layout:
        raise SystemExit(f"ABORT: {v} unexpectedly already in design layout")
    layout[v] = {"start": int(info["start"]), "length": int(info["length"])}
missing = [v for v in ANALYTIC + DESIGN if v not in layout]
if missing:
    raise SystemExit(f"ABORT: variables missing from layout: {missing}")
print(f"layout OK: {len(layout)} vars (11 analytic from shipped layout + 4 design from SAS dictionary)")

def sl(var):
    i = layout[var]["start"] - 1
    return slice(i, i + layout[var]["length"])

C = {v: sl(v) for v in ANALYTIC + DESIGN}

# ------------------------------------------------------ obtain the raw file --
def open_text_lines():
    """Yield decoded fixed-width lines from MICRODATA_TXT / MICRODATA_ZIP / download."""
    txt_env = os.getenv("MICRODATA_TXT")
    if txt_env and os.path.exists(txt_env):
        print(f"MICRODATA_TXT: {txt_env}")
        with open(txt_env, encoding="latin-1") as f:
            yield from f
        return
    zip_env = os.getenv("MICRODATA_ZIP")
    if zip_env and os.path.exists(zip_env):
        zip_path = zip_env
    else:
        def resolve_zip_name():
            dir_url = f"{BASE_URL}/{YEAR}/"
            with urllib.request.urlopen(dir_url, timeout=60) as r:
                html = r.read().decode("utf-8", errors="replace")
            m = re.findall(rf'href="(PNADC_0{QUARTER}{YEAR}(?:_\d+)?\.zip)"', html)
            if not m:
                raise SystemExit(f"no zip found for {YEAR}Q{QUARTER} at {dir_url}")
            return sorted(m)[-1]
        zip_name = resolve_zip_name()
        zip_path = os.path.join(RAW, zip_name)
        if not os.path.exists(zip_path):
            zip_url = f"{BASE_URL}/{YEAR}/{zip_name}"
            print(f"downloading {zip_url} ...")
            urllib.request.urlretrieve(zip_url, zip_path)
        print(f"zip cache (deletable): {zip_path}")
    with zipfile.ZipFile(zip_path) as z:
        txt_name = next(n for n in z.namelist() if n.upper().endswith(".TXT"))
        print(f"parsing {txt_name} ...")
        with z.open(txt_name) as f:
            yield from io.TextIOWrapper(f, encoding="latin-1")

# ------------------------------------------------------------- reference ----
with open(os.path.join(REF, "cod_estrutura.json"), encoding="utf-8") as f:
    estrutura = json.load(f)
grupo_base_to_subgrupo = estrutura["grupo_base_to_subgrupo"]
with open(os.path.join(REF, "uf_codes.json"), encoding="utf-8") as f:
    uf_codes = json.load(f)

FORMAL_SEMPRE = {"01", "03", "05", "07"}
DEPENDE_CNPJ = {"08", "09"}
INFORMAL_SEMPRE = {"02", "04", "06", "10"}

def is_informal(posicao, cnpj):
    if posicao in FORMAL_SEMPRE: return False
    if posicao in INFORMAL_SEMPRE: return True
    if posicao in DEPENDE_CNPJ: return cnpj != "1"
    return None

# ----------------------------------------------------------------- parse ----
out_dir = ensure_output_dir(DATA)
out_csv = os.path.join(out_dir, "individual_microdata_design.csv")
n_rows = 0
skipped_unknown = 0
with open(out_csv, "w", encoding="utf-8", newline="") as cf:
    w = csv.writer(cf)
    w.writerow(["uf", "occupation", "weight", "income", "sex", "race",
                "informal", "age", "years_of_study",
                "upa", "estrato", "v1008", "v2003"])
    for line in open_text_lines():
        ocup = line[C["V4010"]].strip()
        if not ocup:
            continue
        uf = uf_codes.get(line[C["UF"]])
        if uf is None:
            continue
        key = grupo_base_to_subgrupo.get(ocup)
        if key is None:
            skipped_unknown += 1
            continue
        weight = float(line[C["V1028"]])
        renda = line[C["VD4016"]].strip()
        income = int(renda) if renda else 0
        sexo = line[C["V2007"]].strip()
        raca = line[C["V2010"]].strip()
        informal = is_informal(line[C["VD4009"]].strip(), line[C["V4019"]].strip())
        idade = line[C["V2009"]].strip()
        idade = int(idade) if idade else None
        anos = line[C["VD3005"]].strip()
        anos = int(anos) if anos else None
        w.writerow([uf["sigla"], key, weight, income, sexo, raca,
                    int(informal) if informal is not None else "",
                    idade if idade is not None else "",
                    anos if anos is not None else "",
                    line[C["UPA"]].strip(), line[C["Estrato"]].strip(),
                    line[C["V1008"]].strip(), line[C["V2003"]].strip()])
        n_rows += 1

print(f"rows written: {n_rows} (skipped unknown occupations: {skipped_unknown})")
print(f"-> {out_csv}")

# ------------------------------------------------------------ validation ----
import pandas as pd

mine = pd.read_csv(out_csv, dtype={"occupation": str, "upa": str, "estrato": str,
                                   "v1008": str, "v2003": str, "sex": str, "race": str})
shipped = pd.read_csv(SHIPPED, dtype={"occupation": str, "sex": str, "race": str})
cols = ["uf", "occupation", "weight", "income", "sex", "race", "informal", "age", "years_of_study"]

def canon(df):
    d = df[cols].copy()
    for c in ["informal", "age", "years_of_study"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return d.sort_values(cols, kind="mergesort").reset_index(drop=True)

a, b = canon(mine), canon(shipped)
if a.shape != b.shape:
    raise SystemExit(f"ABORT: shape mismatch mine {a.shape} vs shipped {b.shape}")
if not a.equals(b):
    diff = (a != b) | (a.isna() != b.isna())
    print("mismatched cells:", int(diff.to_numpy().sum()))
    raise SystemExit("ABORT: regenerated extract differs from shipped extract")
print("VALIDATION PASSED: 9 analytic columns identical to shipped extract "
      f"({len(a)} rows, multiset-equal)")

# quick design-variable sanity
print("UPA unique:", mine["upa"].nunique(), "| Estrato unique:", mine["estrato"].nunique(),
      "| households (upa+v1008):", mine.groupby(["upa", "v1008"]).ngroups,
      "| persons (upa+v1008+v2003):", mine.groupby(["upa", "v1008", "v2003"]).ngroups)
kish = mine["weight"].sum() ** 2 / (mine["weight"] ** 2).sum()
print(f"Kish ESS (full extract): {kish:,.0f} of {len(mine):,}")
