import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.0-flash-001"


def _call_openrouter(messages: list, system: str = None) -> str:
    """Helper to call OpenRouter and return raw content string."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set")

    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.extend(messages)

    response = requests.post(
        url=OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3005",
            "X-Title": "CleanCodeX",
        },
        data=json.dumps({"model": MODEL, "messages": msgs}),
        timeout=15
    )
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content'].strip()


def _clean_json(raw: str) -> str:
    """Strip markdown code fences from LLM JSON output."""
    if raw.startswith("```"):
        lines = raw.splitlines()
        # Remove first and last fence lines
        inner = lines[1:-1] if lines[-1].startswith("```") else lines[1:]
        return "\n".join(inner).strip()
    return raw


def get_ai_suggestions(code: str) -> list:
    """
    Returns 2-3 AI code review suggestions as structured issue dicts.
    Each has: line (int), message (str), type (str), symbol (str).
    """
    if not OPENROUTER_API_KEY:
        return []  # Silent fail — no API key noise in suggestions

    try:
        system = (
            "You are a senior Python code reviewer. "
            "Analyze the provided Python code and return ONLY a valid JSON array "
            "of 2-3 specific, actionable improvement suggestions. "
            "Each object must have: "
            "  'line' (int, the relevant line number), "
            "  'message' (string, what to improve and why), "
            "  'type' ('warning' or 'info'), "
            "  'symbol' ('ai-review'). "
            "Focus on: readability, PEP8, edge cases, performance. "
            "Do NOT include markdown, do NOT include any text outside the JSON array."
        )
        raw = _call_openrouter(
            [{"role": "user", "content": f"Review this Python code:\n\n```python\n{code}\n```"}],
            system=system
        )
        cleaned = _clean_json(raw)
        suggestions = json.loads(cleaned)
        # Validate structure
        valid = []
        for s in suggestions:
            if isinstance(s, dict) and "message" in s:
                valid.append({
                    "line": s.get("line", 1),
                    "message": s.get("message", ""),
                    "type": s.get("type", "info"),
                    "symbol": "ai-review",
                    "column": 1
                })
        return valid
    except Exception as e:
        print(f"[AI Service] get_ai_suggestions error: {e}")
        return []


def get_ai_fix(code: str, issue: dict) -> dict:
    """
    Given a specific issue dict (line, message, type, symbol),
    returns AI-generated fix: { explanation, fixed_code, diff_hint }
    """
    if not OPENROUTER_API_KEY:
        return {
            "explanation": "No OpenRouter API key configured.",
            "fixed_code": code,
            "diff_hint": ""
        }

    line = issue.get("line", 1)
    message = issue.get("message", "Unknown issue")
    symbol = issue.get("symbol", "")

    lines = code.splitlines()
    # Show context: 3 lines before and after the issue line
    start = max(0, line - 4)
    end = min(len(lines), line + 3)
    context = "\n".join(
        f"{'>>>' if i + 1 == line else '   '} {i + 1}: {lines[i]}"
        for i in range(start, end)
    )

    prompt = (
        f"I have this Python code issue:\n"
        f"Issue: {message}\n"
        f"Rule: {symbol}\n"
        f"On line {line}:\n\n"
        f"```\n{context}\n```\n\n"
        f"Full code:\n```python\n{code}\n```\n\n"
        f"Provide:\n"
        f"1. A short explanation (1-2 sentences) of WHY this is an issue\n"
        f"2. The complete fixed version of the code\n\n"
        f"Respond ONLY in this JSON format:\n"
        f'{{"explanation": "...", "fixed_code": "..."}}'
    )

    try:
        system = (
            "You are an expert Python developer and code quality specialist. "
            "You provide precise, actionable code fixes. "
            "Always respond with valid JSON only. No markdown. No extra text."
        )
        raw = _call_openrouter(
            [{"role": "user", "content": prompt}],
            system=system
        )
        cleaned = _clean_json(raw)
        result = json.loads(cleaned)
        return {
            "explanation": result.get("explanation", ""),
            "fixed_code": result.get("fixed_code", code),
            "diff_hint": f"Fix for: {message}"
        }
    except Exception as e:
        print(f"[AI Service] get_ai_fix error: {e}")
        return {
            "explanation": f"AI fix failed: {str(e)}",
            "fixed_code": code,
            "diff_hint": ""
        }
