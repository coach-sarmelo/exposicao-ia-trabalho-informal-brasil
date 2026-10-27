#!/usr/bin/env python3
"""Reproducibility script for the Brazilian labor market AI exposure dashboard.

Optionally renders `Quarto/index.qmd` via Quarto CLI, reads the individual
microdata CSV (PNAD Contínua 2026Q1) and associated metadata, serializes columns
into compact binary buffers, Base64-encodes them, and embeds or updates the
`window.DASH_DATA` block inside `docs/index.html`.

Adheres to:
  - AEA DCAS Open Science reproducibility standards
  - PEP 8 and idiomatic Python patterns (typing, context managers, EAFP)
  - Zero external dependency footprint (pure Python 3 standard library)

Usage:
    python scripts/build_dashboard.py
    python scripts/build_dashboard.py --render
    python scripts/build_dashboard.py --check
    python scripts/build_dashboard.py --dry-run
    python scripts/build_dashboard.py --help
"""
from __future__ import annotations

import argparse
import array
import base64
import csv
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

# Shared path resolution helper
SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
DEFAULT_HTML_PATH = REPO_ROOT / "docs" / "index.html"
DEFAULT_QMD_PATH = REPO_ROOT / "Quarto" / "index.qmd"

sys.path.insert(0, str(SCRIPTS_DIR))
from _paths import resolve_data_dir  # noqa: E402

# Canonical label definitions
SEX_LABELS: list[str] = ["Homem", "Mulher"]
RACE_LABELS: dict[str, str] = {
    "1": "Branca",
    "2": "Preta",
    "3": "Amarela",
    "4": "Parda",
    "5": "Indígena",
    "9": "Ignorada",
}
FORM_LABELS: list[str] = ["Formal", "Informal"]

REQUIRED_COLUMNS: set[str] = {
    "uf",
    "occupation",
    "weight",
    "income",
    "sex",
    "race",
    "informal",
    "age",
    "years_of_study",
}


def find_quarto_executable() -> Optional[str]:
    """Locate the Quarto CLI executable on PATH or standard install locations."""
    found = shutil.which("quarto")
    if found:
        return found

    candidates = [
        Path.home() / "AppData" / "Local" / "Programs" / "Quarto" / "bin" / "quarto.exe",
        Path("C:/Program Files/Quarto/bin/quarto.exe"),
        Path("/usr/local/bin/quarto"),
        Path("/opt/quarto/bin/quarto"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def render_quarto_dashboard(
    qmd_path: Path | str = DEFAULT_QMD_PATH,
    html_out_path: Path | str = DEFAULT_HTML_PATH,
) -> Path:
    """Render Quarto/index.qmd to HTML and copy it to docs/index.html.

    Args:
        qmd_path: Path to source .qmd file.
        html_out_path: Destination HTML file path (typically docs/index.html).

    Returns:
        Path to the rendered destination HTML file.

    Raises:
        FileNotFoundError: If Quarto CLI or source .qmd file is missing.
        RuntimeError: If `quarto render` exits with a non-zero status.
    """
    qmd = Path(qmd_path).resolve()
    if not qmd.is_file():
        raise FileNotFoundError(f"Quarto source file not found: {qmd}")

    quarto_bin = find_quarto_executable()
    if not quarto_bin:
        raise FileNotFoundError("Quarto CLI executable not found on PATH or standard directories.")

    cmd = [quarto_bin, "render", str(qmd)]
    res = subprocess.run(cmd, cwd=str(qmd.parent), capture_output=True, text=True, check=False)
    if res.returncode != 0:
        raise RuntimeError(
            f"quarto render failed (exit {res.returncode}):\n{res.stdout}\n{res.stderr}"
        )

    rendered_html = qmd.with_suffix(".html")
    if not rendered_html.is_file():
        raise FileNotFoundError(f"Expected rendered HTML not found at: {rendered_html}")

    dest = Path(html_out_path).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(rendered_html, dest)
    return dest


def load_reference_data(data_dir: Path | str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load geographic and econometric reference JSON dictionaries.

    Args:
        data_dir: Root data directory containing reference/ and analysis/.

    Returns:
        Tuple of (uf_codes, scores) dictionaries.

    Raises:
        FileNotFoundError: If required JSON files are absent.
    """
    data_path = Path(data_dir)
    uf_path = data_path / "reference" / "uf_codes.json"
    scores_path = data_path / "analysis" / "scores.json"

    if not uf_path.is_file():
        raise FileNotFoundError(f"Missing geographic reference: {uf_path}")
    if not scores_path.is_file():
        raise FileNotFoundError(f"Missing exposure scores: {scores_path}")

    with open(uf_path, "r", encoding="utf-8") as f:
        uf_codes = json.load(f)

    with open(scores_path, "r", encoding="utf-8") as f:
        scores = json.load(f)

    return uf_codes, scores


def build_geo_metadata(uf_codes: dict[str, Any]) -> tuple[list[str], list[str], list[int]]:
    """Build sorted list of UFs, unique regions, and the UF-to-region index mapping.

    Args:
        uf_codes: Dictionary mapping IBGE codes to state metadata.

    Returns:
        Tuple of:
          - ufs: Sorted list of 2-letter state abbreviations (27 total)
          - regions: Sorted list of geographic macro-regions (5 total)
          - uf_region: Integer array of region indices corresponding to each UF
    """
    uf_info = {entry["sigla"]: entry for entry in uf_codes.values()}
    ufs = sorted(uf_info.keys())
    regions = sorted({entry["regiao"] for entry in uf_info.values()})
    region_to_idx = {reg: idx for idx, reg in enumerate(regions)}
    uf_region = [region_to_idx[uf_info[uf]["regiao"]] for uf in ufs]
    return ufs, regions, uf_region


def build_occupation_metadata(
    csv_path: Path | str,
    scores: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, int], list[str], int]:
    """Scan microdata for unique occupation codes and compute total row count.

    Args:
        csv_path: Path to individual_microdata.csv.
        scores: Dictionary mapping occupation codes to name and exposure score.

    Returns:
        Tuple of:
          - occs: List of dicts [{"code": str, "name": str, "expo": float | None}]
          - occ_map: Mapping from occupation code string to integer index
          - no_score_occs: Sorted list of occupation codes without exposure score
          - row_count: Number of microdata records
    """
    unique_occs: set[str] = set()
    row_count = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        missing = REQUIRED_COLUMNS - set(header)
        if missing:
            raise ValueError(f"Missing required columns in {csv_path}: {sorted(missing)}")
        occ_idx = header.index("occupation")
        for row in reader:
            row_count += 1
            unique_occs.add(row[occ_idx])

    occs: list[dict[str, Any]] = []
    for code in sorted(unique_occs):
        if code in scores:
            name = scores[code].get("name", f"Ocupação COD {code}")
            expo = scores[code].get("exposure")
        else:
            name = f"Ocupação COD {code}"
            expo = None
        occs.append({"code": code, "name": name, "expo": expo})

    occ_map = {entry["code"]: idx for idx, entry in enumerate(occs)}
    no_score_occs = sorted([entry["code"] for entry in occs if entry["expo"] is None])
    return occs, occ_map, no_score_occs, row_count


def serialize_microdata(
    csv_path: Path | str,
    uf_map: dict[str, int],
    occ_map: dict[str, int],
    no_score_set: set[str],
    row_count: int
) -> tuple[int, dict[str, str], dict[str, int]]:
    """Stream microdata rows and serialize each column into compact binary/Base64.

    Binary layouts:
      - uf:   Uint8 (1 byte/row)
      - occ:  Uint8 (1 byte/row)
      - inc:  Uint32 little-endian (4 bytes/row)
      - w:    Float32 little-endian (4 bytes/row)
      - demo: Uint8 bitfield (1 byte/row): (race << 2) | (female << 1) | informal
      - age:  Uint8 (1 byte/row)
      - edu:  Uint8 (1 byte/row)

    Args:
        csv_path: Path to individual_microdata.csv.
        uf_map: State abbreviation to integer index mapping.
        occ_map: Occupation code to integer index mapping.
        no_score_set: Set of occupation codes lacking an exposure score.
        row_count: Total pre-calculated number of rows.

    Returns:
        Tuple of:
          - row_count: Total number of individuals
          - b64_payload: Dictionary of Base64 strings for each serialized column
          - stats: Dictionary with row counts for diagnostic metadata
    """
    uf_bytes = bytearray(row_count)
    occ_bytes = bytearray(row_count)
    demo_bytes = bytearray(row_count)
    age_bytes = bytearray(row_count)
    edu_bytes = bytearray(row_count)

    inc_arr = array.array("I", [0] * row_count)
    w_arr = array.array("f", [0.0] * row_count)

    no_score_rows = 0
    zero_income_rows = 0

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        col = {name: idx for idx, name in enumerate(header)}

        for idx, row in enumerate(reader):
            uf_val = row[col["uf"]]
            occ_val = row[col["occupation"]]
            w_val = float(row[col["weight"]])
            inc_val = int(float(row[col["income"]]))
            sex_val = int(row[col["sex"]])
            race_val = int(row[col["race"]])
            inf_val = int(row[col["informal"]])
            age_val = int(row[col["age"]])
            edu_val = int(row[col["years_of_study"]])

            uf_bytes[idx] = uf_map[uf_val]
            occ_bytes[idx] = occ_map[occ_val]

            inc_arr[idx] = inc_val
            if inc_val == 0:
                zero_income_rows += 1

            w_arr[idx] = w_val

            if occ_val in no_score_set:
                no_score_rows += 1

            female = 1 if sex_val == 2 else 0
            demo_bytes[idx] = (race_val << 2) | (female << 1) | inf_val
            age_bytes[idx] = age_val
            edu_bytes[idx] = edu_val

    # Ensure little-endian encoding on all architectures
    if sys.byteorder != "little":
        inc_arr.byteswap()
        w_arr.byteswap()

    inc_bytes = inc_arr.tobytes()
    w_bytes = w_arr.tobytes()

    b64_payload = {
        "uf": base64.b64encode(uf_bytes).decode("ascii"),
        "occ": base64.b64encode(occ_bytes).decode("ascii"),
        "inc": base64.b64encode(inc_bytes).decode("ascii"),
        "w": base64.b64encode(w_bytes).decode("ascii"),
        "demo": base64.b64encode(demo_bytes).decode("ascii"),
        "age": base64.b64encode(age_bytes).decode("ascii"),
        "edu": base64.b64encode(edu_bytes).decode("ascii"),
    }

    stats = {
        "noScoreRows": no_score_rows,
        "zeroIncomeRows": zero_income_rows,
    }
    return row_count, b64_payload, stats


def build_dash_data(
    data_dir: Path | str,
    quarter: str = "2026Q1",
    timestamp: Optional[str] = None
) -> dict[str, Any]:
    """Construct full DASH_DATA payload dictionary matching the client contract.

    Args:
        data_dir: Root directory of data/.
        quarter: Survey reference quarter identifier.
        timestamp: Optional ISO/date timestamp for builtAt field.

    Returns:
        Structured DASH_DATA dictionary ready for JSON serialization.
    """
    data_path = Path(data_dir)
    csv_path = data_path / "analysis" / "individual_microdata.csv"
    if not csv_path.is_file():
        raise FileNotFoundError(f"Microdata CSV not found at: {csv_path}")

    uf_codes, scores = load_reference_data(data_path)
    ufs, regions, uf_region = build_geo_metadata(uf_codes)
    uf_map = {uf: idx for idx, uf in enumerate(ufs)}

    occs, occ_map, no_score_occs, row_count = build_occupation_metadata(csv_path, scores)
    no_score_set = set(no_score_occs)

    row_count, b64_payload, stats = serialize_microdata(
        csv_path, uf_map, occ_map, no_score_set, row_count
    )

    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    meta = {
        "quarter": quarter,
        "noScoreRows": stats["noScoreRows"],
        "noScoreOccs": no_score_occs,
        "zeroIncomeRows": stats["zeroIncomeRows"],
        "minCellN": 30,
        "scatterTarget": 4000,
        "builtAt": timestamp,
    }

    dash_data: dict[str, Any] = {
        "n": row_count,
        "b64": b64_payload,
        "ufs": ufs,
        "regions": regions,
        "ufRegion": uf_region,
        "occs": occs,
        "sexLabels": SEX_LABELS,
        "raceLabels": RACE_LABELS,
        "formLabels": FORM_LABELS,
        "meta": meta,
    }
    return dash_data


def embed_dash_data_in_html(html_path: Path | str, dash_data: dict[str, Any]) -> int:
    """Inject or update the `window.DASH_DATA` script block in target HTML file.

    Supports both updating an existing `<script>window.DASH_DATA = ...</script>` block
    and generating/inserting one into an HTML file where it does not yet exist.

    Args:
        html_path: Path to index.html dashboard file.
        dash_data: Dictionary containing the structured dashboard payload.

    Returns:
        Total bytes written to the HTML file.

    Raises:
        FileNotFoundError: If the target HTML file does not exist.
    """
    path = Path(html_path)
    if not path.is_file():
        raise FileNotFoundError(f"HTML target not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Compact JSON representation without unnecessary whitespace
    serialized_json = json.dumps(dash_data, separators=(",", ":"), ensure_ascii=False)
    replacement = f"<script>window.DASH_DATA = {serialized_json};</script>"

    # Pattern matching any script tag containing window.DASH_DATA assignment
    pattern = re.compile(r"<script\b[^>]*>\s*window\.DASH_DATA\s*=\s*[\s\S]*?;\s*<\/script>")
    if pattern.search(content):
        updated_content = pattern.sub(lambda _: replacement, content, count=1)
    elif "<!-- DASH_DATA -->" in content:
        updated_content = content.replace("<!-- DASH_DATA -->", replacement, 1)
    elif '<script src="https://cdn.plot.ly' in content:
        updated_content = content.replace(
            '<script src="https://cdn.plot.ly',
            f"{replacement}\n<script src=\"https://cdn.plot.ly",
            1
        )
    elif "</head>" in content:
        updated_content = content.replace("</head>", f"{replacement}\n</head>", 1)
    elif "</body>" in content:
        updated_content = content.replace("</body>", f"{replacement}\n</body>", 1)
    else:
        updated_content = content + "\n" + replacement

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        bytes_written = f.write(updated_content)

    return bytes_written


def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Build and embed binary microdata payload into docs/index.html."
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Custom root data directory (defaults to auto-detected via _paths.py).",
    )
    parser.add_argument(
        "--html",
        type=str,
        default=None,
        help="Path to dashboard index.html (defaults to <repo>/docs/index.html).",
    )
    parser.add_argument(
        "--qmd",
        type=str,
        default=None,
        help="Path to Quarto index.qmd (defaults to <repo>/Quarto/index.qmd).",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Render Quarto/index.qmd to docs/index.html before embedding DASH_DATA.",
    )
    parser.add_argument(
        "--quarter",
        type=str,
        default="2026Q1",
        help="Quarter string identifier (default: 2026Q1).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build and validate DASH_DATA without writing to HTML.",
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default=None,
        help="Optional destination path to export raw JSON payload.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify existing HTML DASH_DATA matches source microdata bit-for-bit.",
    )
    return parser.parse_args(args)


def main(argv: Optional[list[str]] = None) -> int:
    """Main execution function."""
    args = parse_args(argv)

    data_dir = Path(args.data_dir) if args.data_dir else Path(resolve_data_dir())
    html_path = Path(args.html) if args.html else DEFAULT_HTML_PATH
    qmd_path = Path(args.qmd) if args.qmd else DEFAULT_QMD_PATH

    print("=" * 70)
    print("REPRODUCIBILITY PIPELINE: BUILD INTERACTIVE DASHBOARD DATA")
    print("=" * 70)
    print(f"  Data Directory : {data_dir}")
    print(f"  Target HTML    : {html_path}")
    print(f"  Reference Period: {args.quarter}")

    if args.render:
        print(f"\nRendering Quarto dashboard from {qmd_path}...")
        render_quarto_dashboard(qmd_path, html_path)
        print(f"  [OK] Quarto render complete -> {html_path}")

    start_time = datetime.datetime.now()
    dash_data = build_dash_data(data_dir, quarter=args.quarter)
    elapsed = (datetime.datetime.now() - start_time).total_seconds()

    print(f"\n[BUILD COMPLETE in {elapsed:.2f}s]")
    print(f"  Sample Size (n)   : {dash_data['n']:,} individuals")
    print(f"  Occupations       : {len(dash_data['occs'])} COD codes")
    print(f"  Unscored Occs     : {len(dash_data['meta']['noScoreOccs'])} ({dash_data['meta']['noScoreRows']:,} rows)")
    print(f"  Zero-Income Rows  : {dash_data['meta']['zeroIncomeRows']:,}")
    print(f"  Geographic Units  : {len(dash_data['ufs'])} UFs across {len(dash_data['regions'])} regions")

    if args.json_out:
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(dash_data, f, ensure_ascii=False)
        print(f"  Exported JSON to  : {out_path}")

    if args.check:
        print("\nVerifying parity against existing HTML payload...")
        if not html_path.is_file():
            print(f"  [FAIL] Target HTML not found: {html_path}")
            return 1

        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        m = re.search(r"<script\b[^>]*>\s*window\.DASH_DATA\s*=\s*(\{[\s\S]*?\});?\s*<\/script>", html_content)
        if not m:
            print("  [FAIL] Could not extract DASH_DATA from target HTML.")
            return 1
        existing_data = json.loads(m.group(1))

        # Check binary columns
        all_match = True
        for col_name in ["uf", "occ", "inc", "w", "demo", "age", "edu"]:
            if dash_data["b64"].get(col_name) != existing_data.get("b64", {}).get(col_name):
                print(f"  [MISMATCH] Column '{col_name}' base64 payload diverges.")
                all_match = False

        # Check metadata & dimension arrays
        for key in ["n", "ufs", "regions", "ufRegion", "occs", "sexLabels", "raceLabels", "formLabels"]:
            if dash_data.get(key) != existing_data.get(key):
                print(f"  [MISMATCH] Field '{key}' diverges.")
                all_match = False

        # Check meta object (excluding dynamic builtAt timestamp)
        for meta_key in ["quarter", "noScoreRows", "noScoreOccs", "zeroIncomeRows", "minCellN", "scatterTarget"]:
            if dash_data.get("meta", {}).get(meta_key) != existing_data.get("meta", {}).get(meta_key):
                print(f"  [MISMATCH] Meta field '{meta_key}' diverges.")
                all_match = False

        if all_match:
            print("  [PASS] 100% Bit-for-bit parity confirmed against target HTML.")
            return 0
        else:
            print("  [FAIL] Discrepancies detected between generated data and HTML.")
            return 1

    if args.dry_run:
        print("\n[DRY RUN] Target HTML was not modified.")
        return 0

    print(f"\nEmbedding payload into {html_path}...")
    bytes_written = embed_dash_data_in_html(html_path, dash_data)
    print(f"  [SUCCESS] Updated {html_path} ({bytes_written:,} characters).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
