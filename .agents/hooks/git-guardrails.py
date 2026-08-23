#!/usr/bin/env python3
"""
Git & Path Guardrails Hook (PreToolUse)

Dual-compatible with Claude Code and Antigravity CLI (agy).
Blocks destructive git commands and hardcoded machine paths in replication scripts.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

_GO = (r"(?:-C\s+\S+\s+|-c\s+\S+\s+|--git-dir(?:=\S+\s+|\s+\S+\s+)|"
       r"--work-tree(?:=\S+\s+|\s+\S+\s+)|--no-pager\s+|--paginate\s+|-p\s+)*")

GIT_DENY = [
    (re.compile(r"\bgit\s+" + _GO + r"reset\s+--hard\b"),
     "git reset --hard discards uncommitted work irrecoverably.",
     "Use `git stash` (recoverable) or reset specific paths."),
    (re.compile(r"\bgit\s+" + _GO + r"clean\b.*(--force\b|(?<![\w-])-[a-z]*f)"),
     "git clean -f/--force deletes UNTRACKED files — including data not yet committed.",
     "Inspect with `git clean -n` first; delete specific paths by hand."),
    (re.compile(r"\bgit\s+" + _GO + r"push\b.*(--force(?![\w-])|(?<!-)\s-f\b)"),
     "git push --force clobbers remote history.",
     "Use `git push --force-with-lease` if you truly must rewrite a branch."),
    (re.compile(r"\bgit\s+" + _GO + r"add\s+(?:--\s+)?(-A\b|--all\b|\.(?:\s|$)|:/)"),
     "Blanket staging (git add -A / . / -- . / :/) can stage data, secrets, or settings.local.json. "
     "The /commit skill forbids it.",
     "Stage specific files: `git add path/to/file ...`."),
    (re.compile(r"\bgit\s+" + _GO + r"(checkout|restore)\s+(--\s+)?\.(?:\s|$)"),
     "Mass discard of working-tree changes is irreversible.",
     "Discard specific files, or `git stash` to keep them recoverable."),
]

HARDCODED_PATH = re.compile(r"(/Users/[^/\s'\")]+|/home/[^/\s'\")]+|[A-Za-z]:\\\\Users\\\\[^\\\s'\"]+)")
CODE_EXT = {".R", ".r", ".qmd", ".do", ".py", ".Rmd"}


def respond_deny(reason: str, is_antigravity: bool) -> None:
    if is_antigravity:
        json.dump({"decision": "deny", "reason": reason}, sys.stdout)
    else:
        json.dump({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }}, sys.stdout)


def respond_allow(is_antigravity: bool) -> None:
    if is_antigravity:
        json.dump({"decision": "allow"}, sys.stdout)


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        data = json.loads(raw)
    except Exception:
        return 0

    is_antigravity = "toolCall" in data

    if is_antigravity:
        tool_call = data.get("toolCall", {}) or {}
        tool = tool_call.get("name", "")
        args = tool_call.get("args", {}) or {}
        cmd = args.get("CommandLine", "") or ""
        fp = args.get("TargetFile", "") or args.get("AbsolutePath", "") or ""
        content_candidates = [
            args.get("CodeContent", ""),
            args.get("ReplacementContent", "")
        ]
        for chunk in args.get("ReplacementChunks", []) or []:
            content_candidates.append((chunk or {}).get("ReplacementContent", ""))
    else:
        tool = data.get("tool_name", "")
        ti = data.get("tool_input", {}) or {}
        cmd = ti.get("command", "") or ""
        fp = ti.get("file_path", "") or ""
        content_candidates = [
            ti.get("content", ""),
            ti.get("new_string", "")
        ]
        for e in ti.get("edits", []) or []:
            content_candidates.append((e or {}).get("new_string", ""))

    # 1. Shell command checks
    if tool in ("Bash", "run_command"):
        for pat, reason, alt in GIT_DENY:
            if pat.search(cmd):
                respond_deny(
                    f"Blocked by git-guardrails: {reason} {alt} (override: run in manual terminal outside agent.)",
                    is_antigravity
                )
                return 0
        respond_allow(is_antigravity)
        return 0

    # 2. File edit checks
    if tool in ("Write", "Edit", "MultiEdit", "write_to_file", "replace_file_content", "multi_replace_file_content"):
        if Path(fp).suffix in CODE_EXT:
            for content in content_candidates:
                if isinstance(content, str):
                    m = HARDCODED_PATH.search(content)
                    if m:
                        msg = (f"Hardcoded machine path '{m.group(0)}' in {Path(fp).name} "
                               f"breaks replication packages. Use relative paths or config variables.")
                        if os.environ.get("CLAUDE_STRICT_PATHS", "") == "1" or os.environ.get("AGY_STRICT_PATHS", "") == "1":
                            respond_deny(f"Blocked (STRICT_PATHS=1): {msg}", is_antigravity)
                            return 0
                        else:
                            sys.stderr.write(f"[git-guardrails] WARNING: {msg}\n")
                        break

    respond_allow(is_antigravity)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
