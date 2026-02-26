from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 🛡️ 門番：サテライトUI（React）からのあらゆる信号を受け入れ、他を拒絶する
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧠 ジェネシスの記憶
stats = {"current_count": 0}

# 📡 WebSocket マネージャー
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

@app.get("/")
def read_root():
    return {"status": "TORUS GENESIS CORE ACTIVE", "version": "17.2 FINAL"}

@app.get("/api/health")
def health_check():
    return {"status": "online", "core": "TORUS_GENESIS_V17.2"}

@app.post("/api/ingress")
async def ingress(data: dict = Body(...)):
    global stats
    if data.get("type") == "RESET":
        stats["current_count"] = 0
        await manager.broadcast("RESET")
        return {"status": "RESET_COMPLETE", "current_count": 0}
    
    stats["current_count"] += 1
    # リアルタイム同期信号を射出
    await manager.broadcast(str(stats["current_count"]))
    return {"status": "ACCEPTED", "current_count": stats["current_count"]}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
