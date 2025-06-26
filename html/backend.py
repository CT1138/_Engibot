from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
import uvicorn
import subprocess
import asyncio

app = FastAPI()
service_name = "engibot.service"
host_ip = "192.168.68.40"
port = 8080

stats = {
    "cpu": 0.0,
    "memory": 0.0,
    "guilds": 0,
    "ip": "0.0.0.0"
}

@app.get("/logs", response_class=PlainTextResponse)
async def logs_endpoint(lines: int = 100):
    logs = get_latest_logs(lines)
    return logs

@app.get("/stats")
async def get_stats():
    return JSONResponse(content=stats)

@app.post("/webhook/update")
async def update_stats(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Validate incoming data - update only known keys
    valid_keys = {"cpu", "memory", "guilds", "ip"}
    updated = False

    for key in valid_keys:
        if key in data:
            stats[key] = data[key]
            updated = True

    if not updated:
        raise HTTPException(status_code=400, detail="No valid keys to update")

    return {"status": "success", "updated": {k: stats[k] for k in valid_keys if k in data}}

def get_latest_logs(lines=100):
    try:
        result = subprocess.run(
            ["journalctl", "-u", service_name, "-n", str(lines), "--no-pager", "--output=short"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error fetching logs: {e.stderr}")

async def stream_journalctl():
    process = await asyncio.create_subprocess_exec(
        "journalctl", "-u", service_name, "-f", "--no-pager", "--output=short",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            yield f"data: {line.decode('utf-8')}\n\n"
    finally:
        process.kill()

if __name__ == "__main__":
    uvicorn.run(app, host=host_ip, port=port)
