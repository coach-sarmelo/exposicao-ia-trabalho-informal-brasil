#!/usr/bin/env python3
"""
Numeric-Claim Reconciliation Hook (PostToolUse)

Dual-compatible with Claude Code and Antigravity CLI (agy).
Event-driven half of the cross-artifact dependency graph: the moment an
analysis script or an `_outputs/` artifact changes, the manuscript's
numeric claims that depend on it may be STALE. Instead of waiting for the
nightly reproducibility Routine, this hook surfaces the staleness
immediately so the author re-runs /audit-reproducibility before relying
on the affected tables.

Fires on Write/Edit to:
  - scripts/**/*.{R,do,py,jl}        (analysis code)
  - scripts/**/_outputs/**           (regenerated outputs)
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import hashlib
from pathlib import Path

WATCH = re.compile(r"(^|[\\/])scripts[\\/].*\.(R|r|do|py|jl)$|(^|[\\/])scripts[\\/].*[\\/]_outputs[\\/]", re.IGNORECASE)
THROTTLE_S = 300


def state_dir() -> Path:
    pd = os.environ.get("AGY_PROJECT_DIR") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    h = hashlib.md5(pd.encode()).hexdigest()[:8] if pd else "default"
    d = Path.home() / ".gemini" / "antigravity" / "sessions" / h
    d.mkdir(parents=True, exist_ok=True)
    return d


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        data = json.loads(raw)
    except Exception:
        return 0

    is_antigravity = "toolCall" in data or "workspacePaths" in data

    if is_antigravity:
        tool_call = data.get("toolCall", {}) or {}
        args = tool_call.get("args", {}) or {}
        fp = args.get("TargetFile", "") or args.get("AbsolutePath", "") or ""
        ws_paths = data.get("workspacePaths", []) or []
        project_dir = ws_paths[0] if ws_paths else os.getcwd()
    else:
        ti = data.get("tool_input", {}) or {}
        fp = ti.get("file_path", "") or ""
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "") or data.get("cwd", "") or os.getcwd()

    if not fp or not WATCH.search(fp):
        if is_antigravity:
            json.dump({}, sys.stdout)
        return 0

    passports = sorted((Path(project_dir) / "quality_reports" / "passports").glob("*.yaml"))
    if not passports:
        if is_antigravity:
            json.dump({}, sys.stdout)
        return 0  # no claims tracked → nothing to reconcile

    try:
        changed = str(Path(fp).resolve().relative_to(Path(project_dir).resolve()))
    except Exception:
        changed = Path(fp).name

    # Throttle: one nudge per changed file per THROTTLE_S.
    st_path = state_dir() / "claim-reconcile-state.json"
    try:
        st = json.loads(st_path.read_text(encoding="utf-8"))
    except Exception:
        st = {}
    now = time.time()
    if now - st.get(changed, 0) < THROTTLE_S:
        if is_antigravity:
            json.dump({}, sys.stdout)
        return 0
    st[changed] = now
    try:
        st_path.write_text(json.dumps(st), encoding="utf-8")
    except Exception:
        pass

    # Count passport claims that reference this file (best-effort text match).
    affected = []
    for p in passports:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        hits = sum(1 for ln in text.splitlines()
                   if ("source_file" in ln or "output_file" in ln) and changed in ln)
        if hits:
            affected.append((p.name, hits))
    if not affected:
        if is_antigravity:
            json.dump({}, sys.stdout)
        return 0

    total = sum(h for _, h in affected)
    where = ", ".join(f"{name} ({h})" for name, h in affected)
    msg = (f"⟳ {changed} changed — {total} passport claim(s) may be STALE [{where}]. "
           f"Run /audit-reproducibility before relying on the affected tables.")

    if is_antigravity:
        sys.stderr.write(f"\n[claim-reconcile] {msg}\n")
        json.dump({}, sys.stdout)
    else:
        json.dump({
            "systemMessage": msg,
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    f"A tracked analysis input ({changed}) was just modified. "
                    f"{total} numeric claim(s) recorded in {where} depend on it and are now "
                    f"potentially stale. Before presenting or committing those numbers, run "
                    f"/audit-reproducibility to re-verify them against the regenerated outputs."
                ),
            },
        }, sys.stdout)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)  # fail open
