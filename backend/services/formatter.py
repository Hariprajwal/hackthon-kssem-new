import black

def run_formatter(code: str):
    try:
        formatted = black.format_str(code, mode=black.FileMode())
        return formatted
    except Exception as e:
        return code # Return original code if formatting fails
