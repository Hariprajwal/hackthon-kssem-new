import ast

def analyze_ast(code: str):
    issues = []
    try:
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            # Check for camelCase function names (Python standard is snake_case)
            if isinstance(node, ast.FunctionDef):
                if any(c.isupper() for c in node.name):
                    issues.append({
                        "line": node.lineno,
                        "column": node.col_offset + 1,
                        "message": f"Function name '{node.name}' uses camelCase. Python standard is snake_case.",
                        "type": "warning",
                        "symbol": "naming-convention"
                    })
                
                # Check for long functions (> 20 lines)
                if node.end_lineno - node.lineno > 20:
                    issues.append({
                        "line": node.lineno,
                        "column": node.col_offset + 1,
                        "message": f"Function '{node.name}' is too long ({node.end_lineno - node.lineno} lines). Consider refactoring.",
                        "type": "info",
                        "symbol": "long-function"
                    })

            # Check for complexity (too many nested loops)
            if isinstance(node, (ast.For, ast.While)):
                loop_level = 0
                curr = node
                while hasattr(curr, 'parent') or isinstance(curr, (ast.For, ast.While)):
                   # Simple depth check is complex with ast.walk, but we can do it recursively if needed
                   break 

        return issues
    except SyntaxError as e:
        return [{"line": e.lineno, "message": f"Syntax Error: {e.msg}", "type": "error"}]
    except Exception as e:
        return []
