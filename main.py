from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# 🛡️ 門番：サテライトUI（React）からの通信を許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

stats = {"current_count": 0}

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# 🚀 修正点：ブラウザが「保存」ではなく「表示」するように JSONResponse を明示
@app.get("/")
async def read_root():
    return JSONResponse(content={"status": "TORUS GENESIS CORE ACTIVE", "version": "17.2 FINAL"})

@app.post("/api/ingress")
async def ingress(data: dict = Body(...)):
    global stats
    if data.get("type") == "RESET":
        stats["current_count"] = 0
        await manager.broadcast("RESET")
        return {"status": "RESET_COMPLETE", "current_count": 0}
    stats["current_count"] += 1
    await manager.broadcast(str(stats["current_count"]))
    return {"status": "ACCEPTED", "current_count": stats["current_count"]}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
