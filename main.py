import subprocess
import time
import sys
import os

def run_backend():
    print("🚀 Starting FastAPI Backend...")
    return subprocess.Popen([sys.executable, "backend/server.py"])

def run_frontend():
    print("🌐 Starting React Frontend on port 3005...")
    env = os.environ.copy()
    env["PORT"] = "3005"
    # Use npm.cmd on Windows, npm on other platforms
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    return subprocess.Popen([npm_cmd, "start"], cwd="frontend", env=env)

if __name__ == "__main__":
    try:
        backend_proc = run_backend()
        time.sleep(2) # Give backend a moment to start
        frontend_proc = run_frontend()
        
        print("\n✅ CleanCodeX is running!")
        print("Backend: http://localhost:8000")
        print("Frontend: http://localhost:3005")
        print("\nPress Ctrl+C to stop both servers.")
        
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping CleanCodeX servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        sys.exit(0)
