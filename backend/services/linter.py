import subprocess
import tempfile
import os
import json

def run_linter(code: str):
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w') as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        # Run pylint and capture output
        # --output-format=json is useful for parsing
        result = subprocess.run(
            ["pylint", "--output-format=json", tmp_path],
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            lint_results = json.loads(result.stdout)
            # Map pylint results to our format
            return [
                {
                    "line": issue.get("line"),
                    "column": issue.get("column") + 1,
                    "message": issue.get("message"),
                    "type": issue.get("type"),
                    "symbol": issue.get("symbol")
                }
                for issue in lint_results
            ]
        return []
    except Exception as e:
        print(f"Linter error: {e}")
        return [{"line": 1, "message": f"Linter error: {str(e)}", "type": "error"}]
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
