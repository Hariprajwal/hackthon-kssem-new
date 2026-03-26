from fastapi import APIRouter
from pydantic import BaseModel
from ..services.executor import run_code

router = APIRouter()

class CodeRequest(BaseModel):
    code: str

@router.post("/execute")
async def execute_code(request: CodeRequest):
    result = run_code(request.code)
    return {
        "status": "success",
        "stdout": result["stdout"],
        "stderr": result["stderr"],
        "exit_code": result["exit_code"] if "exit_code" in result else 0
    }
