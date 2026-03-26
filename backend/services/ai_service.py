import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def get_ai_suggestions(code: str):
    if not OPENROUTER_API_KEY:
        return [{"id": 0, "type": "info", "message": "API Key missing. Please set OPENROUTER_API_KEY.", "line": 1}]

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "google/gemini-2.0-flash-001",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a senior code reviewer. Analyze the provided Python code and suggest 2-3 specific improvements for readability, performance, or best practices. Format your response STRICTLY as a JSON list of objects, each with 'line' (int), 'message' (string), and 'type' (string, either 'warning' or 'info'). Do not include any other text."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this code:\n\n{code}"
                    }
                ]
            })
        )
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content'].strip()
            # Robust JSON cleaning
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Fallback if AI output is slightly messy
                return [{"line": 1, "message": "AI provided non-JSON suggestions. Try again.", "type": "info"}]
        else:
            print(f"OpenRouter Error: {response.text}")
            error_msg = response.json().get('error', {}).get('message', 'Unknown Error')
            return [{"id": 0, "type": "error", "message": f"AI Error: {error_msg}", "line": 1}]
            
    except Exception as e:
        print(f"AI Service Error: {e}")
        return [{"id": 0, "type": "error", "message": str(e), "line": 1}]
