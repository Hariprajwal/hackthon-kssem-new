from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from backend.routes import lint, format, execute, auth, files
from backend.database import engine
from backend import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CleanCodeX API")

# CORS — allow everything (dev mode)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to CleanCodeX API", "status": "online"}


# ── Flask-Compatible /analyze route ────────────────────────────
class AnalyzeRequest(BaseModel):
    code: str = ""

@app.post("/analyze")
async def analyze_code(req: AnalyzeRequest):
    from backend.services.linter import run_linter
    from backend.services.formatter import run_formatter
    issues = run_linter(req.code)
    formatted = run_formatter(req.code)
    lint_text = "\n".join([f"Line {i['line']}: {i['message']}" for i in issues])
    return {
        "lint": lint_text or "No issues found.",
        "formatted_code": formatted,
        "issue_count": len(issues)
    }


# ── API Routers ─────────────────────────────────────────────────
app.include_router(lint.router,    prefix="/api/lint",    tags=["lint"])
app.include_router(format.router,  prefix="/api/format",  tags=["format"])
app.include_router(execute.router, prefix="/api/execute", tags=["execute"])
app.include_router(auth.router,    prefix="/api/auth",    tags=["auth"])
app.include_router(files.router,   prefix="/api/files",   tags=["files"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
