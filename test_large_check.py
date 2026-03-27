import requests
import time

# Create a "large" code block (approx 1000 lines)
big_code = "\n".join([f"def func_{i}():\n    print({i})\n    x = {i} # Long line just to trigger pylint many times {'a'*100}" for i in range(500)])

url = "http://127.0.0.1:8000/api/lint/check"
print(f"Sending request with {len(big_code)} bytes...")
start = time.time()
try:
    res = requests.post(url, json={"code": big_code}, timeout=30)
    print(f"Status: {res.status_code}")
    print(f"Time Taken: {time.time() - start:.2f}s")
    if res.status_code == 200:
        data = res.json()
        print(f"Issues Found: {len(data['issues'])}")
        print(f"Quality Score: {data['quality_score']}")
    else:
        print(res.text)
except Exception as e:
    print(f"Error: {e}")
