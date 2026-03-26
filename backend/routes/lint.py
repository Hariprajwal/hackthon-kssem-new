from fastapi import APIRouter
from pydantic import BaseModel
from ..services.linter import run_linter
from ..services.ai_service import get_ai_suggestions
from ..services.ast_parser import analyze_ast

router = APIRouter()

class CodeRequest(BaseModel):
    code: str

@router.post("/check")
async def check_code(request: CodeRequest):
    # Get static linting issues
    lint_issues = run_linter(request.code)
    
    # Get AI-powered suggestions
    ai_suggestions = get_ai_suggestions(request.code)
    
    # Get AST analysis
    ast_issues = analyze_ast(request.code)
    
    # Combine results
    combined_issues = lint_issues + ai_suggestions + ast_issues
    
    # Calculate quality score (simple heuristic)
    deduction = len(lint_issues) * 5 + len(ai_suggestions) * 10
    quality_score = max(0, 100 - deduction)
    
    return {
        "issues": combined_issues,
        "quality_score": quality_score
    }
