from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..services.linter import run_linter
from ..services.ast_parser import analyze_ast, auto_fix
from ..services.formatter import run_formatter
from ..services.ai_service import get_ai_suggestions, get_ai_fix

router = APIRouter()

class CodeRequest(BaseModel):
    code: str

class FixRequest(BaseModel):
    code: str
    issues: list = []

class AIFixRequest(BaseModel):
    code: str
    issue: dict


@router.post("/check")
async def check_code(request: CodeRequest):
    """
    Full code analysis: Pylint + AST (9+ checks) + AI review.
    Returns issues list, quality score, and per-category stats.
    """
    # 1. Pylint static check
    lint_issues = run_linter(request.code)

    # 2. Advanced AST analysis (9+ checks)
    ast_issues = analyze_ast(request.code)

    # 3. AI Code Review (async-compatible, but runs sync here)
    ai_issues = get_ai_suggestions(request.code)

    # Combine and deduplicate by (line, first 40 chars of message)
    all_issues = lint_issues + ast_issues + ai_issues
    seen = set()
    unique = []
    for issue in all_issues:
        key = (issue.get("line"), issue.get("message", "")[:40])
        if key not in seen:
            seen.add(key)
            unique.append(issue)

    # Quality score — weighted
    error_count   = sum(1 for i in unique if i.get("type") == "error")
    warning_count = sum(1 for i in unique if i.get("type") == "warning")
    info_count    = sum(1 for i in unique if i.get("type") == "info")
    ai_count      = sum(1 for i in unique if i.get("symbol") == "ai-review")

    # Weighted deduction: errors hit hard, AI insights are mild
    deduction = (error_count * 15) + (warning_count * 6) + (info_count * 2) + (ai_count * 4)
    quality_score = max(0, 100 - deduction)

    # Count auto-fixable issues (have a "fix" key)
    fixable = sum(1 for i in unique if "fix" in i)

    return {
        "issues": unique,
        "quality_score": quality_score,
        "stats": {
            "errors": error_count,
            "warnings": warning_count,
            "info": info_count,
            "ai": ai_count,
            "fixable": fixable,
            "total": len(unique)
        }
    }


@router.post("/autofix")
async def autofix_code(request: FixRequest):
    """Apply all safely auto-fixable issues (e.g. rename camelCase)."""
    issues = request.issues if request.issues else analyze_ast(request.code)
    fixed_code = auto_fix(request.code, issues)
    new_issues = analyze_ast(fixed_code)
    return {
        "fixed_code": fixed_code,
        "original_issue_count": len(issues),
        "remaining_issue_count": len(new_issues)
    }


@router.post("/ai-fix")
async def ai_fix_issue(request: AIFixRequest):
    """
    AI-powered fix for a specific issue.
    Returns: explanation, fixed_code, diff_hint.
    """
    result = get_ai_fix(request.code, request.issue)
    return result


@router.post("/format-diff")
async def format_diff(request: CodeRequest):
    """Return formatted code and a unified diff."""
    import difflib
    original = request.code
    formatted = run_formatter(original)
    diff = list(difflib.unified_diff(
        original.splitlines(keepends=True),
        formatted.splitlines(keepends=True),
        fromfile="original.py",
        tofile="formatted.py"
    ))
    return {
        "formatted_code": formatted,
        "has_changes": original != formatted,
        "diff": "".join(diff)
    }
