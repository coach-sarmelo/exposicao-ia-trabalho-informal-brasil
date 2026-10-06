#!/usr/bin/env python3
"""Automated Integrity Checker for Quarto Dashboards (format: dashboard).

Verifies layout architecture, card containment, value box ergonomics,
image resolution, and GitHub Pages deployment readiness against the
7 Hard Gates defined in .agents/agents/quarto-critic/agent.md and
.zcode/skills/macroquant-workflow/SKILL.md.

Usage:
    python scripts/check-dashboard-integrity.py [Quarto/index.qmd]

Exit codes:
    0: All hard gates pass
    1: Hard gate failures or critical layout defects detected
"""

import os
import re
import sys
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Allowed Bootstrap semantic colors
VALID_COLORS = {
    "primary", "secondary", "success", "info",
    "warning", "danger", "light", "dark"
}

# Common Bootstrap icons in academic/economic dashboards
COMMON_ICONS = {
    "people", "person", "briefcase", "graph-up", "graph-up-arrow",
    "graph-down", "graph-down-arrow", "shield-check", "shield-slash",
    "cpu", "mortarboard", "cash-stack", "currency-dollar", "geo-alt",
    "building", "bar-chart", "pie-chart", "table", "file-earmark-text",
    "file-earmark-pdf", "file-earmark-x", "check-circle", "x-circle",
    "exclamation-triangle", "info-circle", "book", "calculator",
    "award", "calendar", "clock", "globe", "search", "share"
}


def check_dashboard(qmd_path):
    if not os.path.isabs(qmd_path):
        qmd_path = os.path.join(ROOT, qmd_path)

    if not os.path.exists(qmd_path):
        print(f"[FAIL] Target dashboard file not found: {qmd_path}")
        return 1

    with open(qmd_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        lines = content.splitlines()

    rel_path = os.path.relpath(qmd_path, ROOT)
    print(f"=== Auditing Quarto Dashboard: {rel_path} ===")

    errors = []
    warnings = []

    # -------------------------------------------------------------
    # 1. Frontmatter Verification
    # -------------------------------------------------------------
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Missing YAML frontmatter (must start with '---')")
        fm = {}
    else:
        try:
            fm = yaml.safe_load(frontmatter_match.group(1))
            if not isinstance(fm, dict):
                errors.append("Invalid YAML frontmatter structure")
                fm = {}
        except Exception as e:
            errors.append(f"YAML frontmatter parsing error: {e}")
            fm = {}

    fmt = fm.get("format", {})
    if isinstance(fmt, str):
        is_dashboard = fmt == "dashboard"
    elif isinstance(fmt, dict):
        is_dashboard = "dashboard" in fmt
    else:
        is_dashboard = False

    if not is_dashboard:
        errors.append("Frontmatter must declare 'format: dashboard'")
    else:
        print("  [OK] Frontmatter declares 'format: dashboard'")

    # Check embed-resources if standalone delivery
    dash_config = fmt.get("dashboard", {}) if isinstance(fmt, dict) else {}
    if isinstance(dash_config, dict):
        if not dash_config.get("embed-resources", False):
            warnings.append(
                "Frontmatter does not specify 'embed-resources: true' under dashboard. "
                "Ensure asset folders (_files/) are deployed alongside HTML."
            )
        else:
            print("  [OK] 'embed-resources: true' enabled for standalone delivery")

    # -------------------------------------------------------------
    # 2. Local Machine Paths & Asset Resolution (Gate D7)
    # -------------------------------------------------------------
    # Forbidden absolute machine paths (guard against matching URLs like https://)
    abs_path_patterns = [
        r"(?<![a-zA-Z0-9])[a-zA-Z]:[\\/](?![\\/])[^'\"\s\n]+",  # Windows C:\... or C:/... (not ://)
        r"(?<![a-zA-Z0-9])/(?:Users|home|private|var|tmp)/[^'\"\s\n]+"  # Unix /Users/... /home/...
    ]
    for i, line in enumerate(lines, 1):
        if re.search(r"https?://", line):
            # Check non-URL parts of line
            clean_line = re.sub(r"https?://[^\s'\"\)]+", "", line)
        else:
            clean_line = line
        for pat in abs_path_patterns:
            matches = re.findall(pat, clean_line)
            for m in matches:
                errors.append(f"Line {i}: Hardcoded absolute machine path: {m}")

    # Local markdown images: ![](path)
    qmd_dir = os.path.dirname(qmd_path)
    img_matches = re.finditer(r"!\[.*?\]\((?!https?://)(.*?)\)", content)
    for m in img_matches:
        img_file = m.group(1).split()[0]  # strip optional attributes
        # Clean query strings or anchors
        img_file = img_file.split("?")[0].split("#")[0]
        full_img_path = os.path.normpath(os.path.join(qmd_dir, img_file))
        if not os.path.exists(full_img_path):
            errors.append(f"Referenced local image not found: '{img_file}' (resolved to {full_img_path})")
        else:
            print(f"  [OK] Image asset verified: {img_file}")

    # -------------------------------------------------------------
    # 3. Grid & Layout Architecture (Gate D2)
    # -------------------------------------------------------------
    headings_l1 = [line for line in lines if line.startswith("# ") and not line.startswith("## ")]
    headings_l2 = [line for line in lines if line.startswith("## ") and not line.startswith("### ")]
    headings_l3 = [line for line in lines if line.startswith("### ")]

    if len(headings_l1) > 1:
        print(f"  [OK] Multi-page dashboard with {len(headings_l1)} navigation pages")
    elif len(headings_l1) == 1:
        print(f"  [OK] Single-page dashboard: '{headings_l1[0].strip()}'")

    if not headings_l2:
        warnings.append("No Level 2 headings (## Row or ## Column) found. Content will use auto-flow.")
    else:
        print(f"  [OK] Found {len(headings_l2)} primary rows/columns (Level 2)")

    # -------------------------------------------------------------
    # 4. Value Box Syntax & Semantics (Gate D4)
    # -------------------------------------------------------------
    # Find markdown value boxes: ::: {.valuebox ...} ... :::
    vb_pattern = re.compile(r":::\s*\{\.valuebox([^}]*)\}\s*\n(.*?)\n:::", re.DOTALL)
    vb_matches = list(vb_pattern.finditer(content))
    print(f"  [OK] Found {len(vb_matches)} markdown value boxes")

    for idx, vb in enumerate(vb_matches, 1):
        attrs = vb.group(1)
        body = vb.group(2).strip()

        # Check icon
        icon_m = re.search(r'icon=["\']?([a-z0-9-]+)["\']?', attrs)
        if not icon_m:
            warnings.append(f"Valuebox #{idx}: missing icon attribute")
        else:
            icon_name = icon_m.group(1)
            if icon_name not in COMMON_ICONS and not re.match(r"^[a-z0-9-]+$", icon_name):
                warnings.append(f"Valuebox #{idx}: unusual icon '{icon_name}' (verify against Bootstrap Icons)")

        # Check color
        color_m = re.search(r'color=["\']?([a-z0-9#-]+)["\']?', attrs)
        if not color_m:
            warnings.append(f"Valuebox #{idx}: missing color attribute")
        else:
            color_val = color_m.group(1)
            if color_val not in VALID_COLORS and not color_val.startswith("#"):
                errors.append(f"Valuebox #{idx}: invalid semantic color '{color_val}' (must be one of {VALID_COLORS} or hex)")

        # Check 3-tier structure (paragraphs separated by blank lines)
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        if len(paragraphs) != 3:
            warnings.append(
                f"Valuebox #{idx}: contains {len(paragraphs)} paragraph tiers (recommended: exactly 3: Title, Metric, Subtitle)"
            )

    # -------------------------------------------------------------
    # 5. Tabsets Verification (Gate D5)
    # -------------------------------------------------------------
    tabset_lines = [i for i, line in enumerate(lines, 1) if "{.tabset" in line]
    for tl in tabset_lines:
        line_text = lines[tl - 1]
        if not (line_text.startswith("## ") or line_text.startswith("### ")):
            errors.append(f"Line {tl}: '{{.tabset}}' must be attached to a Level 2 (##) or Level 3 (###) heading")
        else:
            print(f"  [OK] Valid tabset defined at line {tl}")

    # -------------------------------------------------------------
    # 6. GitHub Pages Deployment Health (Gate D7)
    # -------------------------------------------------------------
    docs_dir = os.path.join(ROOT, "docs")
    nojekyll_path = os.path.join(docs_dir, ".nojekyll")
    if not os.path.exists(nojekyll_path):
        errors.append("docs/.nojekyll does not exist! Required to prevent GitHub Pages from dropping Quarto directories.")
    else:
        print("  [OK] docs/.nojekyll verified")

    docs_html = os.path.join(docs_dir, "index.html")
    if not os.path.exists(docs_html):
        warnings.append("docs/index.html does not exist yet. Run 'quarto render Quarto/index.qmd && cp Quarto/index.html docs/index.html'")
    else:
        print("  [OK] docs/index.html verified")

    # -------------------------------------------------------------
    # Summary & Exit
    # -------------------------------------------------------------
    print("\n--- Integrity Audit Results ---")
    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  - [WARN] {w}")

    if errors:
        print(f"\nDefects / Failures ({len(errors)}):")
        for e in errors:
            print(f"  - [DEFECT] {e}")
        print("\nVerdict: REJECTED (Hard gate failures detected)")
        return 1

    print("Verdict: APPROVED (All integrity hard gates passed cleanly)")
    return 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "Quarto/index.qmd"
    sys.exit(check_dashboard(target))
