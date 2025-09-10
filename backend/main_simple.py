import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
import uvicorn
from datetime import datetime
import random

# --- 全局变量定义 ---
manager = None

# --- WebSocket连接管理器 ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket连接已建立，当前连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"WebSocket连接已断开，当前连接数: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        if not self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"发送消息失败: {e}")
                disconnected.append(connection)
        
        # 清理断开的连接
        for conn in disconnected:
            self.disconnect(conn)

# --- 模拟数据生成与广播 ---
async def simulate_data_generation():
    await asyncio.sleep(2)
    print("开始模拟数据生成...")
    
    base_price = 100.0
    price = base_price
    
    while True:
        try:
            # 模拟价格波动
            price_change = random.uniform(-0.5, 0.5)
            price = max(90.0, min(110.0, price + price_change))
            
            # 生成模拟K线数据
            open_price = price
            high_price = price + random.uniform(0, 0.3)
            low_price = price - random.uniform(0, 0.3)
            close_price = low_price + random.uniform(0, high_price - low_price)
            volume = random.randint(1000, 10000)
            
            bar_data = {
                "type": "bar",
                "data": {
                    "symbol": "000001",
                    "exchange": "SSE",
                    "datetime": datetime.now().isoformat(),
                    "interval": "1m",
                    "volume": volume,
                    "open_interest": 0,
                    "open_price": round(open_price, 2),
                    "high_price": round(high_price, 2),
                    "low_price": round(low_price, 2),
                    "close_price": round(close_price, 2),
                }
            }
            
            # 广播数据
            if manager:
                await manager.broadcast(json.dumps(bar_data))
                print(f"广播K线数据: {close_price}")
            
            price = close_price  # 更新基础价格
            await asyncio.sleep(2)  # 每2秒生成一次数据
            
        except Exception as e:
            print(f"数据生成错误: {e}")
            await asyncio.sleep(1)

# --- 生命周期管理 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    global manager
    manager = ConnectionManager()
    print("WebSocket管理器初始化成功")
    
    # 启动数据生成任务
    asyncio.create_task(simulate_data_generation())
    print("模拟数据生成任务已启动")
    
    yield
    
    # 关闭时
    print("服务器正在关闭...")

app = FastAPI(lifespan=lifespan, title="VegaTrader Backend", version="1.0.0")

# --- 中间件配置 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API端点 ---
@app.get("/")
async def root():
    return {
        "message": "VegaTrader Server is Running",
        "version": "1.0.0",
        "status": "active",
        "connections": len(manager.active_connections) if manager else 0
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "websocket_connections": len(manager.active_connections) if manager else 0
    }

@app.get("/status")
async def status():
    return {
        "server": "running",
        "websocket_manager": "active" if manager else "inactive",
        "active_connections": len(manager.active_connections) if manager else 0,
        "timestamp": datetime.now().isoformat()
    }

# --- WebSocket端点 ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 保持连接打开，主要用于接收广播数据
            data = await websocket.receive_text()
            print(f"收到WebSocket消息: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket错误: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    print("启动VegaTrader后端服务器...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


