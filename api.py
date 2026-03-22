from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import subprocess, os, json, sys, asyncio

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.websocket("/ws/scan")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # Receive the URL from React
        url = await websocket.receive_text()
        
        # Start main.py and "pipe" the output line by line
        process = subprocess.Popen(
            [sys.executable, "main.py", url],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )

        # Stream the logs to React in real-time
        for line in iter(process.stdout.readline, ""):
            if line:
                await websocket.send_json({"type": "log", "message": line.strip()})
                await asyncio.sleep(0.01) # Small delay to prevent flooding

        process.wait()

        # Once finished, send the final JSON data
        if os.path.exists("reports/latest_audit.json"):
            with open("reports/latest_audit.json", "r") as f:
                final_data = json.load(f)
                await websocket.send_json({"type": "data", "payload": final_data})
                
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        await websocket.close()