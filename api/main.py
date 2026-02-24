from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 🛡️ CORS設定：Satellite UIからの通信を許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🛰️ サーバー内の真実（お化けを防ぐためメモリ上で管理）
stats = {"current_count": 0}

@app.get("/api/health")
def health_check():
    return {"status": "online", "core": "TORUS_GENESIS_V17"}

@app.post("/api/ingress")
async def ingress(data: dict = Body(...)):
    global stats
    # ⚡ RESET信号を受け取った場合のみ 0 に戻す
    if data.get("type") == "RESET":
        stats["current_count"] = 0
        return {"status": "RESET_COMPLETE", "current_count": 0}
    
    # パルスを受信：数値を1だけ増やす
    stats["current_count"] += 1
    return {"status": "ACCEPTED", "current_count": stats["current_count"]}

@app.get("/api/egress")
def egress():
    return {"current_count": stats["current_count"]}
