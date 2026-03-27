from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import asyncio
import tempfile
import os
import sys
import traceback
import subprocess
import threading
from collections import deque
from ..services.executor import run_code

router = APIRouter()

class CodeRequest(BaseModel):
    code: str

@router.post("/execute")
async def execute_code(request: CodeRequest):
    result = run_code(request.code)
    return {
        "status": "success",
        "stdout": result["stdout"],
        "stderr": result["stderr"],
        "exit_code": result.get("exit_code", 0)
    }

@router.websocket("/ws")
async def websocket_execute(websocket: WebSocket):
    await websocket.accept()
    tmp_path = None
    process = None
    try:
        # First message expected is the code
        data = await websocket.receive_json()
        code = data.get("code", "")
        
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w', encoding='utf-8') as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        # On Windows, use subprocess.Popen
        process = subprocess.Popen(
            [sys.executable, "-u", tmp_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        msg_queue = deque()
        
        def thread_read_stream(stream, stream_type):
            try:
                while True:
                    char = stream.read(1)
                    if not char:
                        break
                    msg_queue.append({"type": stream_type, "content": char})
            except Exception as e:
                print(f"Error reading {stream_type}: {e}")

        stdout_thread = threading.Thread(target=thread_read_stream, args=(process.stdout, "stdout"), daemon=True)
        stderr_thread = threading.Thread(target=thread_read_stream, args=(process.stderr, "stderr"), daemon=True)
        
        stdout_thread.start()
        stderr_thread.start()

        async def ws_to_stdin():
            try:
                while True:
                    text_input = await websocket.receive_text()
                    if process and process.stdin:
                        process.stdin.write(text_input + '\n')
                        process.stdin.flush()
            except WebSocketDisconnect:
                pass
            except Exception as e:
                print(f"WS Stdin Error: {e}")

        stdin_task = asyncio.create_task(ws_to_stdin())

        # Main loop to poll process and send queue
        while process.poll() is None or len(msg_queue) > 0:
            while len(msg_queue) > 0:
                msg = msg_queue.popleft()
                await websocket.send_json(msg)
            await asyncio.sleep(0.05)
            
        stdin_task.cancel()
        await websocket.send_json({"type": "exit", "code": process.returncode})
        
    except WebSocketDisconnect:
        pass
    except Exception as e:
        error_msg = traceback.format_exc()
        # Direct print to stderr to bypass any buffering
        sys.stderr.write(f"\nCRITICAL WEBSOCKET ERROR:\n{error_msg}\n")
        sys.stderr.flush()
        try:
            await websocket.send_json({"type": "error", "content": str(e) or "Internal WebSocket Error"})
        except Exception:
            pass
    finally:
        if process and process.poll() is None:
            try:
                process.terminate()
            except Exception:
                pass
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        try:
            await websocket.close()
        except Exception:
            pass
