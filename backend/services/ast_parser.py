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

    # ── 10. Missing imports / undefined names ────────────────────────────────
    # Collect all names that are DEFINED (Store context: assigned, imported, function/class defs)
    defined_names: set = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                defined_names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":
                    defined_names.add(alias.asname or alias.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defined_names.add(node.name)
            for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
                defined_names.add(arg.arg)
            if node.args.vararg:
                defined_names.add(node.args.vararg.arg)
            if node.args.kwarg:
                defined_names.add(node.args.kwarg.arg)
        elif isinstance(node, ast.ClassDef):
            defined_names.add(node.name)
        elif isinstance(node, ast.Global):
            defined_names.update(node.names)
        elif isinstance(node, ast.NamedExpr):
            defined_names.add(node.target.id)
        # Only collect STORE-context names (LHS of assignment, loop vars, etc.)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            defined_names.add(node.id)

    # Python builtins — always available
    _BUILTINS = set(dir(__builtins__)) if isinstance(__builtins__, dict) else set(dir(__builtins__))
    _BUILTINS.update({
        "True", "False", "None", "print", "len", "range", "int", "str", "list", "dict",
        "set", "tuple", "type", "isinstance", "issubclass", "hasattr", "getattr", "setattr",
        "delattr", "callable", "super", "object", "property", "classmethod", "staticmethod",
        "open", "input", "map", "filter", "zip", "enumerate", "sorted", "reversed", "any",
        "all", "min", "max", "sum", "abs", "round", "pow", "hash", "id", "hex", "oct", "bin",
        "chr", "ord", "repr", "vars", "dir", "help", "exit", "quit", "self", "cls",
        "__name__", "__file__", "__doc__", "__package__", "__spec__", "__import__",
        "__builtins__", "__annotations__", "__all__", "__slots__", "__dict__", "__class__",
        "NotImplemented", "Ellipsis", "__debug__",
    })

    # Walk again looking for Name loads that aren't defined
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            name = node.id
            if name not in defined_names and name not in _BUILTINS:
                issues.append({
                    "line":    node.lineno,
                    "column":  node.col_offset + 1,
                    "message": (
                        f"'{name}' is used but not imported or defined. "
                        f"Add 'import {name}' or 'from <module> import {name}' at the top."
                    ),
                    "type":   "error",
                    "symbol": "undefined-name",
                })

    # ── 11. Environment Awareness (Venv / Missing Packages) ──────────────────
    import importlib.util
    import sys

    # Collect base modules being imported (e.g. "PyQt6" from "from PyQt6.QtWidgets import ...")
    imported_base_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_base_modules.add((alias.name.split(".")[0], getattr(node, "lineno", 1), getattr(node, "col_offset", 0)))
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0: # Only check absolute imports
                imported_base_modules.add((node.module.split(".")[0], getattr(node, "lineno", 1), getattr(node, "col_offset", 0)))

    env_path = sys.prefix
    for module_name, lineno, col in imported_base_modules:
        if module_name in _BUILTINS or module_name in sys.builtin_module_names:
            continue
        try:
            # Check if the module exists in the current Python environment
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                issues.append({
                    "line":    lineno,
                    "column":  col + 1,
                    "message": (
                        f"Environment Warning: '{module_name}' is not installed in the active environment "
                        f"({env_path}). If you installed it globally or in a venv, ensure the backend "
                        f"server is running using that specific Python interpreter."
                    ),
                    "type":   "error",
                    "symbol": "missing-environment-package",
                })
        except Exception:
            pass # Ignore malformed import strings or find_spec failures

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
