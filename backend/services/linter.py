import subprocess
import tempfile
import os
import json


def run_linter(code: str) -> list:
    """
    Run Pylint on the given code string and return a list of issue dicts.
    Each issue: { line, column, message, type, symbol }
    
    - Runs with a 30-second timeout to handle large files.
    - Returns an empty list on any failure rather than crashing.
    """
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            suffix=".py", delete=False, mode="w", encoding="utf-8"
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        result = subprocess.run(
            [
                "pylint",
                "--output-format=json",
                "--max-line-length=120",  # Slightly relaxed to avoid noise
                "--disable=C0114,C0115,C0116",  # Suppress missing-module/class/func docstrings (handled by AST)
                "--disable=R0903,R0801",  # Suppress too-few-public-methods, duplicate-code
                tmp_path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.stdout and result.stdout.strip():
            try:
                lint_results = json.loads(result.stdout)
                return [
                    {
                        "line":    issue.get("line", 1),
                        "column":  (issue.get("column") or 0) + 1,
                        "message": issue.get("message", ""),
                        "type":    _map_type(issue.get("type", "C")),
                        "symbol":  issue.get("symbol", ""),
                    }
                    for issue in lint_results
                    if issue.get("type") not in ("R", "C") or issue.get("type") == "E"
                    # Include errors always; filter convention/refactor unless they are errors
                ]
            except (json.JSONDecodeError, ValueError):
                pass

        return []

    except subprocess.TimeoutExpired:
        print("[Linter] Pylint timed out — file too large or complex.")
        return [{"line": 1, "column": 1, "message": "Pylint timed out (file too complex).", "type": "warning", "symbol": "pylint-timeout"}]
    except FileNotFoundError:
        print("[Linter] pylint not found — install with: pip install pylint")
        return []
    except Exception as exc:
        print(f"[Linter] Unexpected error: {exc}")
        return []
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def _map_type(pylint_type: str) -> str:
    """Map Pylint message type letters to our severity strings."""
    return {
        "E": "error",
        "F": "error",   # Fatal
        "W": "warning",
        "C": "info",    # Convention
        "R": "info",    # Refactor
    }.get(pylint_type.upper()[:1] if pylint_type else "C", "info")
