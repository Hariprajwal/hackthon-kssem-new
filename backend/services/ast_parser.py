import ast
import re

def _camel_to_snake(name: str) -> str:
    """Convert camelCase or PascalCase to snake_case."""
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def analyze_ast(code: str):
    """
    Advanced AST analysis for Python code.
    Returns a list of issues with line, column, message, type, symbol, and optional fix.
    """
    issues = []
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [{
            "line": e.lineno or 1,
            "column": e.offset or 1,
            "message": f"Syntax Error: {e.msg}",
            "type": "error",
            "symbol": "syntax-error"
        }]
    except Exception:
        return []

    lines = code.splitlines()

    for node in ast.walk(tree):

        # ── 1. camelCase function names ───────────────────────────────────────
        if isinstance(node, ast.FunctionDef):
            if any(c.isupper() for c in node.name):
                fixed = _camel_to_snake(node.name)
                issues.append({
                    "line": node.lineno,
                    "column": node.col_offset + 1,
                    "message": f"Function '{node.name}' uses camelCase. Rename to '{fixed}'.",
                    "type": "warning",
                    "symbol": "naming-convention",
                    "fix": {"old": node.name, "new": fixed, "kind": "rename"}
                })

        # ── 2. camelCase class names (should be PascalCase) ──────────────────
        if isinstance(node, ast.ClassDef):
            if node.name and node.name[0].islower():
                fixed = node.name[0].upper() + node.name[1:]
                issues.append({
                    "line": node.lineno,
                    "column": node.col_offset + 1,
                    "message": f"Class '{node.name}' should start with uppercase (PascalCase).",
                    "type": "warning",
                    "symbol": "class-naming",
                    "fix": {"old": node.name, "new": fixed, "kind": "rename"}
                })

        # ── 3. Long functions (> 20 lines) ────────────────────────────────────
        if isinstance(node, ast.FunctionDef):
            length = (node.end_lineno or node.lineno) - node.lineno
            if length > 20:
                issues.append({
                    "line": node.lineno,
                    "column": node.col_offset + 1,
                    "message": f"Function '{node.name}' is {length} lines long. PEP8 recommends ≤ 20 lines. Consider refactoring.",
                    "type": "info",
                    "symbol": "long-function"
                })

        # ── 4. Missing docstring in function ─────────────────────────────────
        if isinstance(node, ast.FunctionDef):
            if not node.name.startswith('_'):   # skip private functions
                body = node.body
                has_doc = (
                    body and isinstance(body[0], ast.Expr) and
                    isinstance(body[0].value, ast.Constant) and
                    isinstance(body[0].value.value, str)
                )
                if not has_doc:
                    issues.append({
                        "line": node.lineno,
                        "column": node.col_offset + 1,
                        "message": f"Function '{node.name}' is missing a docstring.",
                        "type": "info",
                        "symbol": "missing-docstring"
                    })

        # ── 5. Missing type hints ─────────────────────────────────────────────
        if isinstance(node, ast.FunctionDef):
            if not node.name.startswith('_') and node.name not in ('__init__',):
                args_without_hint = [
                    a.arg for a in node.args.args
                    if a.annotation is None and a.arg != 'self'
                ]
                if args_without_hint:
                    issues.append({
                        "line": node.lineno,
                        "column": node.col_offset + 1,
                        "message": f"Function '{node.name}' missing type hints for: {', '.join(args_without_hint)}.",
                        "type": "info",
                        "symbol": "missing-type-hints"
                    })

        # ── 6. Bare except ────────────────────────────────────────────────────
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                issues.append({
                    "line": node.lineno,
                    "column": node.col_offset + 1,
                    "message": "Bare 'except:' catches ALL exceptions. Use 'except Exception as e:' instead.",
                    "type": "warning",
                    "symbol": "bare-except"
                })

        # ── 7. Mutable default argument ───────────────────────────────────────
        if isinstance(node, ast.FunctionDef):
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    issues.append({
                        "line": node.lineno,
                        "column": node.col_offset + 1,
                        "message": f"Function '{node.name}' uses a mutable default argument (list/dict/set). Use 'None' instead.",
                        "type": "warning",
                        "symbol": "mutable-default-arg"
                    })
                    break

        # ── 8. Global variables should be UPPER_CASE ─────────────────────────
        if isinstance(node, ast.Module):
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            name = target.id
                            if name[0].islower() and not name.startswith('_'):
                                issues.append({
                                    "line": stmt.lineno,
                                    "column": target.col_offset + 1,
                                    "message": f"Module-level variable '{name}' should be UPPER_CASE (PEP8 constant convention).",
                                    "type": "info",
                                    "symbol": "global-naming"
                                })

    # ── 9. Long lines (> 79 chars) ────────────────────────────────────────────
    for i, line in enumerate(lines, start=1):
        if len(line) > 79:
            issues.append({
                "line": i,
                "column": 80,
                "message": f"Line {i} is {len(line)} characters (PEP8 max is 79).",
                "type": "info",
                "symbol": "line-too-long"
            })

    # Deduplicate by (line, symbol) to avoid noise
    seen = set()
    unique = []
    for issue in issues:
        key = (issue["line"], issue.get("symbol", ""))
        if key not in seen:
            seen.add(key)
            unique.append(issue)

    return unique


def auto_fix(code: str, issues: list) -> str:
    """
    Apply all safe auto-fixes to the code based on reported issues.
    Returns the fixed code.
    """
    fixed = code
    for issue in issues:
        if "fix" in issue and issue["fix"].get("kind") == "rename":
            old = issue["fix"]["old"]
            new = issue["fix"]["new"]
            # Replace all occurrences of the identifier
            fixed = re.sub(r'\b' + re.escape(old) + r'\b', new, fixed)
    return fixed
