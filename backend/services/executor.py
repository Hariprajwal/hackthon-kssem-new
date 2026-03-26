import subprocess
import tempfile
import os

def run_code(code: str):
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w') as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        # Run code and capture output
        # Timeout to prevent infinite loops
        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": "Execution timed out", "stdout": "", "stderr": "Process killed after 5 seconds"}
    except Exception as e:
        return {"error": str(e), "stdout": "", "stderr": str(e)}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
