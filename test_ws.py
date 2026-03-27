import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://127.0.0.1:8000/api/execute/ws"
    async with websockets.connect(uri) as websocket:
        # Send code
        code = """
name = input('Enter name: ')
print(f'Hello {name}!')
"""
        await websocket.send(json.dumps({"code": code}))
        
        # Receive prompt
        msg1 = await websocket.recv()
        print("Received:", msg1)
        
        # Send input
        await websocket.send("Antigravity")
        
        # Receive output
        while True:
            try:
                msg = await websocket.recv()
                data = json.loads(msg)
                print("Received:", data)
                if data["type"] == "exit":
                    break
            except websockets.exceptions.ConnectionClosed:
                break

if __name__ == "__main__":
    asyncio.run(test_ws())
