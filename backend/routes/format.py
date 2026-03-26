from fastapi import APIRouter
from pydantic import BaseModel
from ..services.formatter import run_formatter

router = APIRouter()

class CodeRequest(BaseModel):
    code: str

@router.post("/format")
async def format_code(request: CodeRequest):
    formatted_code = run_formatter(request.code)
    return {"status": "success", "formatted_code": formatted_code}
