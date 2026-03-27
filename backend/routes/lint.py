from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import difflib
from functools import partial

from ..services.linter    import run_linter
from ..services.ast_parser import analyze_ast, auto_fix
from ..services.formatter  import run_formatter
from ..services.ai_service import get_ai_suggestions, get_ai_fix

router = APIRouter()


class CodeRequest(BaseModel):
    code: str

class FixRequest(BaseModel):
    code: str
    issues: List[dict] = []

class AIFixRequest(BaseModel):
    code: str
    issue: dict


def _run_blocking(fn, *args):
    """Run a synchronous function in the default thread pool."""
    return fn(*args)


def _deduplicate_and_cap(all_issues: list, global_cap: int = 100, per_rule_cap: int = 15) -> list:
    """Sort by severity, deduplicate, and cap per-rule + globally."""
    severity = {"error": 0, "warning": 1, "info": 2}
    all_issues.sort(key=lambda x: severity.get(x.get("type", "info"), 2))

    seen = set()
    rule_counts: dict = {}
    unique = []

    for issue in all_issues:
        sym      = issue.get("symbol", "unknown")
        line     = issue.get("line")
        msg_key  = issue.get("message", "")[:50]
        key      = (line, msg_key)

        if key in seen:
            continue
        rule_counts[sym] = rule_counts.get(sym, 0) + 1
        if rule_counts[sym] > per_rule_cap:
            continue
        if len(unique) >= global_cap:
            break

        seen.add(key)
        unique.append(issue)

    return unique


# ── /check ─────────────────────────────────────────────────────────────────────

@router.post("/check")
async def check_code(request: CodeRequest):
    """
    Full code analysis: Pylint + AST (9+ checks) + AI review.
    All slow calls run in threads so we never block the event loop.
    """
    loop = asyncio.get_event_loop()

    # Run the three independent analyses concurrently in thread pool
    lint_task = loop.run_in_executor(None, run_linter, request.code)
    ast_task  = loop.run_in_executor(None, analyze_ast, request.code)
    ai_task   = loop.run_in_executor(None, get_ai_suggestions, request.code)

    lint_issues, ast_issues, ai_issues = await asyncio.gather(
        lint_task, ast_task, ai_task, return_exceptions=True
    )

    # Treat any exception as an empty result (don't fail the whole request)
    lint_issues = lint_issues if isinstance(lint_issues, list) else []
    ast_issues  = ast_issues  if isinstance(ast_issues,  list) else []
    ai_issues   = ai_issues   if isinstance(ai_issues,   list) else []

    unique = _deduplicate_and_cap(lint_issues + ast_issues + ai_issues)

    error_count   = sum(1 for i in unique if i.get("type") == "error")
    warning_count = sum(1 for i in unique if i.get("type") == "warning")
    info_count    = sum(1 for i in unique if i.get("type") == "info")
    ai_count      = sum(1 for i in unique if i.get("symbol") == "ai-review")
    fixable       = sum(1 for i in unique if "fix" in i)

    deduction     = (error_count * 15) + (warning_count * 6) + (info_count * 2) + (ai_count * 4)
    quality_score = max(0, 100 - deduction)

    return {
        "issues":        unique,
        "quality_score": quality_score,
        "stats": {
            "errors":   error_count,
            "warnings": warning_count,
            "info":     info_count,
            "ai":       ai_count,
            "fixable":  fixable,
            "total":    len(unique),
        },
    }


# ── /autofix ───────────────────────────────────────────────────────────────────

@router.post("/autofix")
async def autofix_code(request: FixRequest):
    """Apply all safely auto-fixable issues (e.g. rename camelCase)."""
    loop = asyncio.get_event_loop()

    # Use provided issues; otherwise re-analyze
    issues = request.issues or await loop.run_in_executor(None, analyze_ast, request.code)

    fixed_code  = await loop.run_in_executor(None, auto_fix, request.code, issues)
    new_issues  = await loop.run_in_executor(None, analyze_ast, fixed_code)

    return {
        "fixed_code":             fixed_code,
        "original_issue_count":   len(issues),
        "remaining_issue_count":  len(new_issues),
    }


# ── /ai-fix ────────────────────────────────────────────────────────────────────

@router.post("/ai-fix")
async def ai_fix_issue(request: AIFixRequest):
    """AI-powered fix for a specific issue. Runs in thread pool."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, get_ai_fix, request.code, request.issue)
    return result


# ── /format-diff ───────────────────────────────────────────────────────────────

@router.post("/format-diff")
async def format_diff(request: CodeRequest):
    """Return formatted code and a unified diff."""
    loop = asyncio.get_event_loop()
    formatted = await loop.run_in_executor(None, run_formatter, request.code)

    diff = list(difflib.unified_diff(
        request.code.splitlines(keepends=True),
        formatted.splitlines(keepends=True),
        fromfile="original.py",
        tofile="formatted.py",
    ))

    return {
        "formatted_code": formatted,
        "has_changes":    request.code != formatted,
        "diff":           "".join(diff),
    }
