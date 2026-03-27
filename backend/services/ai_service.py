import os
import re
import json
import requests
import traceback
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.0-flash-001"


def _call_openrouter(messages: list, system: str = None, max_tokens: int = 4096) -> str:
    """Call OpenRouter and return raw content string."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set in .env")

    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.extend(messages)

    payload = {
        "model": MODEL,
        "messages": msgs,
        "max_tokens": max_tokens,
        "temperature": 0.1,  # deterministic output
    }

    response = requests.post(
        url=OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3005",
            "X-Title": "CleanCodeX",
        },
        data=json.dumps(payload),
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def _extract_json_array(raw: str) -> list:
    """Robustly pull a JSON array out of raw LLM text."""
    raw = raw.strip()
    # Strip markdown fences
    raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\n?```$", "", raw, flags=re.MULTILINE)
    raw = raw.strip()

    # Find first '[' and last ']'
    start = raw.find("[")
    end = raw.rfind("]")
    if start == -1 or end == -1 or end <= start:
        return []
    try:
        return json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return []


# ─── AI Suggestions ────────────────────────────────────────────────────────────

def get_ai_suggestions(code: str) -> list:
    """
    Returns up to 5 AI code review suggestions.
    Each: { line, message, type, symbol, column }
    """
    if not OPENROUTER_API_KEY:
        return []

    # Truncate very long code to avoid burning tokens on suggestions
    truncated = code[:8000]

    import sys
    import platform
    env_context = (
        f"== SYSTEM & ENVIRONMENT CONFIGURATION ==\n"
        f"OS: {platform.system()} | Python Version: {sys.version.split()[0]} | Installed Packages: Assume standard library only unless specified.\n"
        f"Execution Layer: Backend (FastAPI) & Subprocess Shell (Not Frontend UI)\n"
        f"Error Origin: STATIC ANALYSIS (Linter)\n"
    )

    system = (
        "You are a senior Python code reviewer. "
        "Respond with ONLY a valid JSON array — no markdown, no extra text. "
        "Each element: {\"line\": int, \"message\": str, \"type\": \"error\"|\"warning\"|\"info\", \"symbol\": \"ai-review\"}. "
        "Give 3-5 specific, actionable suggestions. STRICT RULES:\n"
        "1. Do NOT assume UI frameworks (like PyQt6) are installed or imported unless you see them in the file.\n"
        "2. If an object is used but not imported (e.g. QVBoxLayout), report it as a missing import 'error', do NOT try to rewrite the logic.\n"
        "3. Prioritize 'ImportError' and 'NameError' issues above architectural nitpicks.\n"
        "4. This is an isolated static analysis test. Do not give feedback on how it interacts with external imaginary layers.\n"
    )

    user_msg = (
        f"{env_context}\n\n"
        f"Review this isolated Python code and return a JSON array of suggestions:\n\n```python\n{truncated}\n```"
    )

    try:
        raw = _call_openrouter(
            [{"role": "user", "content": user_msg}],
            system=system,
            max_tokens=1024,
        )
        items = _extract_json_array(raw)
        valid = []
        for s in items:
            if not isinstance(s, dict) or "message" not in s:
                continue
            valid.append({
                "line":    max(1, int(s.get("line", 1))),
                "message": str(s.get("message", "")),
                "type":    s.get("type", "info") if s.get("type") in ("warning", "info", "error") else "info",
                "symbol":  "ai-review",
                "column":  1,
            })
        return valid
    except Exception as exc:
        print(f"[AI] get_ai_suggestions error: {exc}")
        _log_error("get_ai_suggestions", exc, locals())
        return []


# ─── AI Fix ────────────────────────────────────────────────────────────────────

def get_ai_fix(code: str, issue: dict) -> dict:
    """
    Given a specific issue dict, return { explanation, fixed_code, diff_hint }.
    Uses a windowed strategy so the AI never has to regenerate the entire file.
    """
    if not OPENROUTER_API_KEY:
        return {"explanation": "No API key configured.", "fixed_code": code, "diff_hint": ""}

    line_no  = int(issue.get("line", 1))
    message  = issue.get("message", "Unknown issue")
    symbol   = issue.get("symbol", "")

    lines = code.splitlines()
    n = len(lines)

    # 30-line window around the issue
    win_start = max(0, line_no - 16)
    win_end   = min(n, line_no + 15)
    block     = "\n".join(lines[win_start:win_end])

    # Cap full context to avoid request bloat
    context_code = code[:15000] if len(code) > 15000 else code

    import sys
    import platform
    env_context = (
        f"== SYSTEM & ENVIRONMENT CONFIGURATION ==\n"
        f"OS: {platform.system()} | Python Version: {sys.version.split()[0]} | Installed Packages: Assume standard library only unless specified.\n"
        f"Execution Layer: Backend (FastAPI) & Subprocess Shell (Not Frontend UI)\n"
        f"Error Origin: STATIC ANALYSIS (Linter) — Not a Runtime Execution Error.\n"
    )

    prompt = (
        f"Python Static Analysis Issue on line {line_no}:\n"
        f"Error: {message} [{symbol}]\n\n"
        f"{env_context}\n"
        f"== CONTEXT: FULL CODE (READ ONLY) ==\n"
        f"```python\n{context_code}\n```\n\n"
        f"INSTRUCTIONS:\n"
        f"1. AVOID 'MULTI-LAYER CONFUSION': This code is isolated. Do not fix logic across imaginary boundaries (e.g., UI vs OS handling). Fix ONLY the specific error requested.\n"
        f"2. AVOID 'STATIC VS RUNTIME CONFUSION': This is a static analysis error (e.g., import-error, undefined-variable from Pylint/AST). Do NOT try to 'fix' the logic if the issue is just a missing setup or import.\n"
        f"3. FIX IMPORT STYLES: If the error is an undefined variable like `QVBoxLayout()` but `from PyQt6 import QtWidgets` exists, you MUST explicitly import it like `from PyQt6.QtWidgets import QVBoxLayout`.\n"
        f"4. HOW TO REPLY: You must reply with an EXACT SEARCH/REPLACE block. The SEARCH section must match the existing code EXACTLY, character for character.\n\n"
        f"Reply EXACTLY in this format:\n"
        f"EXPLANATION: [One concise sentence explaining why you changed this]\n"
        f"FIX_BLOCK:\n"
        f"<<<<\n"
        f"[exact lines from the original code to replace]\n"
        f"====\n"
        f"[new lines to insert]\n"
        f">>>>\n"
    )

    system = (
        "You are an elite Python engineer specialized in targeted, surgical bug fixes. "
        "You understand that environment differences (OS, missing packages) and static linter errors (undefined variables) require environment/import fixes, not logic rewrites. "
        "Strict adherence to instructions is mandatory. Never return the full file."
    )

    try:
        raw = _call_openrouter(
            [{"role": "user", "content": prompt}],
            system=system,
            max_tokens=2048,
        )

        # 1. Extract explanation
        exp_match = re.search(r"EXPLANATION:\s*(.+?)(?:\n|$)", raw, re.IGNORECASE)
        explanation = exp_match.group(1).strip() if exp_match else "Fix applied."

        # 2. Extract SEARCH/REPLACE blocks
        fix_match = re.search(r"<<<<\n(.*?)\n====\n(.*?)\n>>>>", raw, re.DOTALL | re.IGNORECASE)
        
        fixed_full_code = code
        diff_hint = f"Fixed line {line_no}: {message}"
        
        if fix_match:
            search_text = fix_match.group(1)
            replace_text = fix_match.group(2)
            
            if search_text in code:
                fixed_full_code = code.replace(search_text, replace_text, 1)
            else:
                explanation += " (AI hallucinated exact match; fallback to raw replace attempt.)"
                # Fuzzy fallback or basic append for demo purposes
                fixed_full_code = replace_text + "\n" + code
        else:
            explanation = "AI fix format failed."

        return {
            "explanation": explanation,
            "fixed_code":  fixed_full_code,
            "diff_hint":   diff_hint,
        }

    except Exception as exc:
        print(f"[AI] get_ai_fix error: {exc}")
        _log_error("get_ai_fix", exc, locals())
        return {
            "explanation": f"AI fix failed: {exc}",
            "fixed_code":  code,
            "diff_hint":   "",
        }


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _log_error(fn: str, exc: Exception, ctx: dict):
    """Write errors to ai_error.log for post-mortem debugging."""
    try:
        with open("ai_error.log", "a", encoding="utf-8") as f:
            f.write(f"\n[{fn}] {exc}\n")
            f.write(traceback.format_exc())
            if "raw" in ctx:
                f.write(f"RAW RESPONSE:\n{ctx['raw'][:2000]}\n")
    except Exception:
        pass
