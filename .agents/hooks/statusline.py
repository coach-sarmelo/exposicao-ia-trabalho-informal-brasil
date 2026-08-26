#!/usr/bin/env python3
"""
Statusline & Context Status Hook

Dual-compatible with Antigravity CLI (agy), Antigravity IDE, and Claude Code.
Provides real-time context status:
- Active model
- Git branch and uncommitted changes count
- Active plan & status (DRAFT / APPROVED / COMPLETED)
- Paper / Artifact compilation freshness
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


def _git(cwd: str, *args: str) -> str:
    """Execute git command safely with timeout."""
    try:
        res = subprocess.run(
            ["git", "-C", cwd, *args],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        return res.stdout.strip() if res.returncode == 0 else ""
    except Exception:
        return ""


def get_git_info(cwd: str) -> tuple[str, str]:
    """Retrieve git branch name and dirty modification count."""
    branch = _git(cwd, "branch", "--show-current")
    if not branch:
        # Detached HEAD or fallback
        branch = _git(cwd, "rev-parse", "--short", "HEAD")
    
    status = _git(cwd, "status", "--porcelain")
    if status:
        lines = [ln for ln in status.splitlines() if ln.strip()]
        dirty = f"±{len(lines)}"
    else:
        dirty = ""
    return branch, dirty


def get_active_plan(cwd: str) -> tuple[str, str]:
    """Inspect quality_reports/plans for the most recent plan status."""
    plans_dir = Path(cwd) / "quality_reports" / "plans"
    if not plans_dir.is_dir():
        return "", ""
    
    plan_files = sorted(
        plans_dir.glob("*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    if not plan_files:
        return "", ""

    latest_plan = plan_files[0]
    status = "DRAFT"
    try:
        text = latest_plan.read_text(encoding="utf-8", errors="replace")
        # Match 'Status: <STATUS>' in header/frontmatter
        m = re.search(
            r"^\s*\**\s*status\s*\**\s*:\s*\**\s*(draft|approved|completed|implemented|in[ -]?progress)",
            text,
            re.IGNORECASE | re.MULTILINE,
        )
        if m:
            val = m.group(1).lower()
            if val.startswith(("completed", "implemented")):
                status = "COMPLETED"
            elif val.startswith("approved"):
                status = "APPROVED"
            elif val.startswith("draft"):
                status = "DRAFT"
            else:
                status = "IN-PROGRESS"
        else:
            # Fallback keyword scan
            upper = text.upper()
            if "COMPLETED" in upper:
                status = "COMPLETED"
            elif "APPROVED" in upper:
                status = "APPROVED"
            elif "DRAFT" in upper:
                status = "DRAFT"
    except Exception:
        status = "UNKNOWN"

    return latest_plan.name, status


def get_compilation_status(cwd: str) -> str:
    """Check if primary paper or slide sources need compilation."""
    root = Path(cwd)
    paper_tex = root / "paper" / "main.tex"
    paper_pdf = root / "paper" / "main.pdf"
    
    if paper_tex.exists():
        try:
            if not paper_pdf.exists() or paper_tex.stat().st_mtime > paper_pdf.stat().st_mtime:
                return "paper:uncompiled"
        except Exception:
            pass
    return ""


def main() -> int:
    payload = {}
    if not sys.stdin.isatty():
        try:
            raw_input = sys.stdin.read()
            if raw_input.strip():
                payload = json.loads(raw_input)
        except Exception:
            payload = {}

    # Detect execution environment
    # Antigravity hook payload includes workspacePaths, modelName, or invocationNum
    is_antigravity = "workspacePaths" in payload or "invocationNum" in payload or "modelName" in payload

    # Workspace directory
    ws_paths = payload.get("workspacePaths", [])
    if ws_paths and isinstance(ws_paths, list):
        cwd = ws_paths[0]
    else:
        cwd = (
            payload.get("workspace", {}).get("current_dir")
            or os.environ.get("AGY_PROJECT_DIR")
            or os.environ.get("CLAUDE_PROJECT_DIR")
            or os.getcwd()
        )

    # Model name
    model_name = (
        payload.get("modelName")
        or (payload.get("model") or {}).get("display_name")
        or ""
    )

    # Permission / Execution mode
    perm_mode = payload.get("permission_mode", "")
    mode_badge = ""
    if perm_mode:
        badge_map = {
            "bypassPermissions": "[BYPASS]",
            "acceptEdits": "[AUTO-EDIT]",
            "plan": "[PLAN]",
            "default": "[PROMPT]",
        }
        mode_badge = badge_map.get(perm_mode, f"[{perm_mode}]")

    # Probe environment
    branch, dirty = get_git_info(cwd)
    plan_name, plan_status = get_active_plan(cwd)
    comp_status = get_compilation_status(cwd)

    # Assemble badges
    badges = []
    if mode_badge:
        badges.append(mode_badge)
    if model_name:
        badges.append(model_name)
    if branch:
        badges.append(f"@{branch}{' ' + dirty if dirty else ''}")
    if plan_status:
        badges.append(f"plan:{plan_status.lower()}")
    if comp_status:
        badges.append(comp_status)

    status_line = "  ".join(badges) if badges else "[Status: Ready]"

    if is_antigravity:
        # PreInvocation output contract
        out = {
            "injectSteps": [
                {
                    "ephemeralMessage": f"[Status] {status_line}"
                }
            ]
        }
        json.dump(out, sys.stdout)
    else:
        # Plain text stdout (e.g. Claude Code statusLine or terminal run)
        sys.stdout.write(status_line)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Fail-open
        sys.exit(0)
