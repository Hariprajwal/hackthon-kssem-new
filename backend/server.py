import asyncio
import sys
import uvicorn
import os

# Essential for subprocesses on Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

if __name__ == "__main__":
    # Ensure we are in the root directory or can find the backend package
    # Adding current directory to sys.path if needed
    sys.path.insert(0, os.getcwd())
    
    uvicorn.run(
        "backend.app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=False, 
        loop="asyncio"
    )
