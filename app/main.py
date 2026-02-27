from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 聖域 UI からの全信号を受信許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 脳（メモリ）の初期状態
stats = {"current_count": 0}

@app.get("/")
async def root():
    return {"status": "TORUS GENESIS CORE ACTIVE", "version": "22.0"}

@app.post("/api/ingress")
async def ingress(request: Request):
    global stats
    data = await request.json()
    
    # ⚠️ UI側のRESETボタン と連動してサーバーも浄化
    if data.get("type") == "RESET":
        stats["current_count"] = 0
        return {"status": "RESET_COMPLETE", "current_count": 0}

    # パルス受信: サーバー側でのみ正確に加算
    stats["current_count"] += 1
    return {"status": "ACCEPTED", "current_count": stats["current_count"]}
