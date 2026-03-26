import requests

code = """def myFunc():
    x =  5
    return x"""

# Test Format
print("Testing Format...")
res = requests.post("http://127.0.0.1:8000/api/lint/format-diff", json={"code": code})
print(res.status_code, res.json())

# Test Autofix
print("\nTesting Autofix...")
issues = [{"fix": {"kind": "rename", "old": "myFunc", "new": "my_func"}}]
res2 = requests.post("http://127.0.0.1:8000/api/lint/autofix", json={"code": code, "issues": issues})
print(res2.status_code, res2.json())
