# -*- coding: utf-8 -*-
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import uvicorn
from typing import List
from datetime import datetime, timedelta
import random

# VN.PY相关导入
from vnpy.event import EventEngine, Event
from vnpy.trader.object import BarData, TickData
from vnpy.trader.constant import Exchange, Interval

# --- 1. WebSocket连接管理器 ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print("connection open")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print("connection closed")

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.disconnect(connection)

# --- 2. 全局变量 ---
manager = None
event_engine = None

# --- 3. VN.PY事件处理器 ---
class VnPyDataHandler:
    def __init__(self, broadcast_func, loop):
        self.broadcast = broadcast_func
        self.loop = loop
    
    def on_tick(self, event):
        """处理Tick数据事件"""
        tick: TickData = event.data
        message = {
            "type": "tick",
            "data": {
                "symbol": tick.symbol,
                "exchange": tick.exchange.value if getattr(tick, "exchange", None) else None,
                "datetime": tick.datetime.isoformat() if tick.datetime else None,
                "name": tick.name,
                "volume": tick.volume,
                "open_interest": tick.open_interest,
                "last_price": tick.last_price,
                "last_volume": tick.last_volume,
                "limit_up": tick.limit_up,
                "limit_down": tick.limit_down,
                "open_price": tick.open_price,
                "high_price": tick.high_price,
                "low_price": tick.low_price,
                "pre_close": tick.pre_close,
            }
        }
        asyncio.run_coroutine_threadsafe(self.broadcast(json.dumps(message)), self.loop)
    
    def on_bar(self, event):
        """处理K线数据事件"""
        bar: BarData = event.data
        message = {
            "type": "bar",
            "data": {
                "symbol": bar.symbol,
                "exchange": bar.exchange.value if getattr(bar, "exchange", None) else None,
                "datetime": bar.datetime.isoformat() if bar.datetime else None,
                "interval": bar.interval.value if bar.interval else None,
                "volume": bar.volume,
                "open_interest": bar.open_interest,
                "open_price": bar.open_price,
                "high_price": bar.high_price,
                "low_price": bar.low_price,
                "close_price": bar.close_price,
            }
        }
        asyncio.run_coroutine_threadsafe(self.broadcast(json.dumps(message)), self.loop)

# --- 4. 模拟数据生成与广播 ---
async def simulate_data_loading():
    await asyncio.sleep(3)
    print("开始模拟VN.PY数据事件...")
    
    # 模拟产生一个K线事件
    bar = BarData(
        symbol="000001",
        exchange=Exchange.SSE,
        datetime=datetime.now().replace(second=0, microsecond=0),
        interval=Interval.MINUTE,
        open_price=100.0,
        high_price=100.5,
        low_price=99.5,
        close_price=100.2,
        volume=10000,
        gateway_name="LOCAL"
    )
    
    # 每隔2秒生成一根"1分钟K线"并广播
    while True:
        # 以上一根的收盘价作为开盘价
        open_price = bar.close_price
        # 增加价格波动范围，使K线图更明显
        delta = random.uniform(-3.0, 3.0)
        close_price = max(1.0, open_price + delta)
        
        # 根据开收盘确定高低点，并增加一定随机性
        high_price = max(open_price, close_price) + random.uniform(0, 2.0)
        low_price = min(open_price, close_price) - random.uniform(0, 2.0)
        
        # 随机成交量
        volume = random.randint(2000, 20000)
        
        # 推进时间轴（按分钟递增）
        bar.datetime = bar.datetime + timedelta(minutes=1)
        
        # 更新bar字段
        bar.open_price = round(open_price, 2)
        bar.high_price = round(high_price, 2)
        bar.low_price = round(low_price, 2)
        bar.close_price = round(close_price, 2)
        bar.volume = volume
        
        # 调试日志
        print(f"BAR {bar.datetime.isoformat()} O:{bar.open_price} H:{bar.high_price} L:{bar.low_price} C:{bar.close_price} V:{bar.volume}")
        
        event = Event("EVENT_BAR", bar)
        event_engine.put(event)
        await asyncio.sleep(2)

# --- 5. 生命周期管理 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    global manager, event_engine
    manager = ConnectionManager()
    
    # 初始化vn.py事件引擎
    event_engine = EventEngine()

    # 获取当前事件循环
    loop = asyncio.get_running_loop()

    # 创建事件处理器
    data_handler = VnPyDataHandler(manager.broadcast, loop)
    
    # 注册事件处理函数
    event_engine.register("EVENT_TICK", data_handler.on_tick)
    event_engine.register("EVENT_BAR", data_handler.on_bar)
    
    print("VN.PY事件引擎初始化成功。")
    
    # 启动事件引擎
    event_engine.start()

    # 启动一个任务来模拟数据加载
    asyncio.create_task(simulate_data_loading())
    
    yield
    
    # 关闭时
    if event_engine:
        event_engine.stop()

app = FastAPI(lifespan=lifespan)

# --- 6. 中间件配置 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 7. API端点 ---
@app.get("/")
async def root():
    return {"message": "VegaTrader Server is Running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# --- 8. WebSocket端点 ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 保持连接打开，主要接收广播数据
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

