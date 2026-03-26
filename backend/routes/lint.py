from fastapi import APIRouter
from pydantic import BaseModel
from ..services.linter import run_linter
from ..services.ast_parser import analyze_ast, auto_fix
from ..services.formatter import run_formatter

router = APIRouter()

class CodeRequest(BaseModel):
    code: str

class FixRequest(BaseModel):
    code: str
    issues: list = []

@router.post("/check")
async def check_code(request: CodeRequest):
    # 1. Pylint static check
    lint_issues = run_linter(request.code)

    # 2. Advanced AST analysis (9+ checks)
    ast_issues = analyze_ast(request.code)

    # Combine — deduplicate on same line+message
    combined = lint_issues + ast_issues
    seen = set()
    unique = []
    for issue in combined:
        key = (issue.get("line"), issue.get("message", "")[:40])
        if key not in seen:
            seen.add(key)
            unique.append(issue)

    # Quality score
    error_count   = sum(1 for i in unique if i.get("type") == "error")
    warning_count = sum(1 for i in unique if i.get("type") == "warning")
    info_count    = sum(1 for i in unique if i.get("type") == "info")
    deduction = error_count * 15 + warning_count * 5 + info_count * 2
    quality_score = max(0, 100 - deduction)

    # Count fixable issues
    fixable = sum(1 for i in unique if "fix" in i)

    return {
        "issues": unique,
        "quality_score": quality_score,
        "stats": {
            "errors": error_count,
            "warnings": warning_count,
            "info": info_count,
            "fixable": fixable
        }
    }

@router.post("/autofix")
async def autofix_code(request: FixRequest):
    """Apply all safe auto-fixes (rename camelCase, etc.)."""
    issues = request.issues if request.issues else analyze_ast(request.code)
    fixed_code = auto_fix(request.code, issues)

    # Re-run analysis on fixed code to confirm improvements
    new_issues = analyze_ast(fixed_code)

    return {
        "fixed_code": fixed_code,
        "original_issue_count": len(issues),
        "remaining_issue_count": len(new_issues)
    }

@router.post("/format-diff")
async def format_diff(request: CodeRequest):
    """Return formatted code alongside a line-by-line diff."""
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
