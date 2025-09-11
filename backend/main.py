# -*- coding: utf-8 -*-
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import uvicorn
from typing import List
from datetime import datetime, timedelta
import random

# VN.PY相关导入
try:
    from vnpy.event import EventEngine, Event
    from vnpy.trader.object import BarData, TickData
    from vnpy.trader.constant import Exchange, Interval
except Exception:
    # 简化降级版本，便于本地无 vn.py 仍可运行
    class Event:
        def __init__(self, type_, data):
            self.type = type_
            self.data = data

    class EventEngine:
        def __init__(self):
            self._handlers = {}
            self._running = False

        def register(self, type_, handler):
            self._handlers.setdefault(type_, []).append(handler)

        def start(self):
            self._running = True

        def stop(self):
            self._running = False

        def put(self, event: Event):
            for h in self._handlers.get(event.type, []):
                try:
                    h(event)
                except Exception:
                    pass

    class Exchange:
        SSE = type('E', (), {'value': 'SSE'})()

    class Interval:
        MINUTE = type('I', (), {'value': '1m'})()

    class TickData:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class BarData:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

# 数据服务相关导入
from data_service.akshare_client import AKShareClient
from data_service.data_converter import DataConverter
from data_service.vnpy_database import VnpyDatabaseManager
# from models.bar_data import DataDownloadRequest, DataStatusResponse, BarDataModel

# 回测服务相关导入
from backtest_service.backtest_engine import BacktestManager
from backtest_service.strategy_manager import StrategyManager
from backtest_service.indicators import TechnicalIndicators

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
akshare_client = None
data_converter = None
db_manager = None
backtest_manager = None
strategy_manager = None
technical_indicators = None

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
    global manager, event_engine, akshare_client, data_converter, db_manager, backtest_manager, strategy_manager, technical_indicators
    manager = ConnectionManager()
    
    # 初始化数据服务组件
    akshare_client = AKShareClient()
    data_converter = DataConverter()
    db_manager = VnpyDatabaseManager()
    
    # 初始化回测服务组件
    backtest_manager = BacktestManager()
    strategy_manager = StrategyManager()
    technical_indicators = TechnicalIndicators()
    
    # 数据库已在初始化时自动创建表结构
        # await db_manager.initialize_database()
    print("数据库初始化成功。")
    print("回测服务组件初始化成功。")
    
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

# --- 8. 数据管理API ---
@app.post("/api/data/download")
async def download_data(request: dict):
    """下载股票数据"""
    try:
        print(f"DEBUG: 接收到的请求参数: {request}")
        print(f"DEBUG: period参数值: {request['period']}")
        
        # 使用AKShare客户端获取数据
        raw_data = await akshare_client.get_stock_data(
            symbol=request["symbol"],
            period=request["period"],
            start_date=request.get("start_date"),
            end_date=request.get("end_date")
        )
        
        if raw_data is None or len(raw_data) == 0:
            return {"success": False, "message": "未获取到数据"}
        
        # 转换数据格式
        bar_data_list = data_converter.akshare_to_vnpy_bars(
            raw_data, 
            symbol=request["symbol"],
            exchange=request["exchange"],
            interval=request["period"]
        )
        
        # 保存到数据库
        success = db_manager.save_bar_data(bar_data_list)
        saved_count = len(bar_data_list) if success else 0
        
        return {
            "success": True,
            "message": f"成功下载并保存 {saved_count} 条数据",
            "count": saved_count
        }
    except Exception as e:
        return {"success": False, "message": f"下载失败: {str(e)}"}

@app.post("/api/data/download/futures")
async def download_futures_data(request: Request):
    """下载期货数据"""
    # 解析JSON请求体
    body = await request.json()
    try:
        print(f"DEBUG: 接收到的期货数据请求参数: {body}")
        
        # 使用AKShare客户端获取期货数据
        try:
            raw_data = await akshare_client.get_futures_data(
                symbol=body["symbol"],
                start_date=body.get("start_date"),
                end_date=body.get("end_date")
            )
            print(f"DEBUG: 获取到的原始数据行数: {len(raw_data) if raw_data is not None else 0}")
            if raw_data is not None and len(raw_data) > 0:
                print(f"DEBUG: 原始数据列名: {raw_data.columns.tolist()}")
        except Exception as e:
            import traceback
            print(f"ERROR: 获取期货数据时出错: {str(e)}")
            print(f"ERROR: 详细错误信息: {traceback.format_exc()}")
            return {"success": False, "message": f"获取期货数据失败: {str(e)}"}
        
        if raw_data is None or len(raw_data) == 0:
            return {"success": False, "message": "未获取到期货数据"}
        
        # 转换数据格式 - 期货使用SHFE交易所，日线数据
        bar_data_list = data_converter.akshare_to_vnpy_bars(
            raw_data,
            symbol=body["symbol"],
            exchange="SHFE",
            interval="1d"
        )
        
        # 保存到数据库
        success = db_manager.save_bar_data(bar_data_list)
        saved_count = len(bar_data_list) if success else 0
        
        return {
            "success": True,
            "message": f"成功下载并保存期货数据 {saved_count} 条",
            "count": saved_count
        }
    except Exception as e:
        import traceback
        print(f"ERROR: 期货数据下载接口出错: {str(e)}")
        print(f"ERROR: 详细错误信息: {traceback.format_exc()}")
        return {"success": False, "message": f"下载期货数据失败: {str(e)}"}

@app.get("/api/data/query")
async def query_data(
    symbol: str,
    exchange: str = "SSE",
    interval: str = "1m",
    start: str = None,
    end: str = None,
    limit: int = 1000
):
    """查询K线数据"""
    try:
        # 转换参数
        from vnpy.trader.constant import Exchange, Interval
        exchange_obj = data_converter._get_vnpy_exchange(exchange)
        interval_obj = data_converter._get_vnpy_interval(interval)
        
        # 解析时间参数
        start_dt = datetime.fromisoformat(start) if start else None
        end_dt = datetime.fromisoformat(end) if end else None
        
        # 查询数据
        bar_data_list = db_manager.load_bar_data(
            symbol=symbol,
            exchange=exchange_obj,
            interval=interval_obj,
            start=start_dt,
            end=end_dt
        )
        
        # 限制返回数量
        if len(bar_data_list) > limit:
            bar_data_list = bar_data_list[-limit:]
        
        # 转换为字典格式
        result = data_converter.vnpy_to_dict_list(bar_data_list)
        
        return {
            "success": True,
            "data": result,
            "count": len(result)
        }
    except Exception as e:
        return {"success": False, "message": f"查询失败: {str(e)}"}

@app.get("/api/data/overview")
async def get_data_overview():
    """获取数据概览"""
    try:
        overview = db_manager.get_data_overview()
        return {"success": True, "data": overview}
    except Exception as e:
        return {"success": False, "message": f"获取概览失败: {str(e)}"}

@app.delete("/api/data/delete")
async def delete_data(
    symbol: str,
    exchange: str = "SSE",
    interval: str = "1m"
):
    """删除指定合约的数据"""
    try:
        from vnpy.trader.constant import Exchange, Interval
        exchange_obj = data_converter._get_vnpy_exchange(exchange)
        interval_obj = data_converter._get_vnpy_interval(interval)
        
        deleted_count = db_manager.delete_bar_data(
            symbol=symbol,
            exchange=exchange_obj,
            interval=interval_obj
        )
        
        return {
            "success": True,
            "message": f"成功删除 {deleted_count} 条数据",
            "count": deleted_count
        }
    except Exception as e:
        return {"success": False, "message": f"删除失败: {str(e)}"}

@app.get("/api/data/symbols")
async def get_supported_symbols():
    """获取支持的股票代码列表"""
    try:
        symbols = await akshare_client.get_supported_symbols()
        return {"success": True, "data": symbols}
    except Exception as e:
        return {"success": False, "message": f"获取失败: {str(e)}"}

@app.get("/api/data/status")
async def get_data_status(symbol: str, exchange: str = "SSE", interval: str = "1m"):
    """获取数据状态"""
    try:
        from vnpy.trader.constant import Exchange, Interval
        exchange_obj = data_converter._get_vnpy_exchange(exchange)
        interval_obj = data_converter._get_vnpy_interval(interval)
        
        count = db_manager.get_bar_count(
            symbol=symbol,
            exchange=exchange_obj,
            interval=interval_obj
        )
        
        latest_bar = db_manager.get_newest_bar_data(
            symbol=symbol,
            exchange=exchange_obj,
            interval=interval_obj
        )
        
        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "exchange": exchange,
                "interval": interval,
                "count": count,
                "latest_datetime": latest_bar.datetime if latest_bar else None,
                "has_data": count > 0
            }
        }
    except Exception as e:
        return {"success": False, "message": f"获取状态失败: {str(e)}"}

# --- 9. 回测管理API ---
@app.get("/api/backtest/strategies")
async def get_strategies():
    """获取可用策略列表"""
    try:
        strategies = strategy_manager.get_all_strategies()
        return {"success": True, "data": strategies}
    except Exception as e:
        return {"success": False, "message": f"获取策略列表失败: {str(e)}"}

@app.get("/api/backtest/strategy/{strategy_name}")
async def get_strategy_info(strategy_name: str):
    """获取策略详细信息"""
    try:
        strategy_info = strategy_manager.get_strategy_info(strategy_name)
        if strategy_info:
            return {"success": True, "data": strategy_info}
        else:
            return {"success": False, "message": "策略不存在"}
    except Exception as e:
        return {"success": False, "message": f"获取策略信息失败: {str(e)}"}

@app.post("/api/backtest/run")
async def run_backtest(request: dict):
    """运行回测"""
    try:
        # 验证请求参数
        required_fields = ['strategy_name', 'symbol', 'exchange', 'interval', 'start_date', 'end_date']
        for field in required_fields:
            if field not in request:
                return {"success": False, "message": f"缺少必要参数: {field}"}
        
        # 验证策略是否存在
        if not strategy_manager.has_strategy(request['strategy_name']):
            return {"success": False, "message": "策略不存在"}
        
        # 验证策略参数
        setting = request.get('setting', {})
        validation_result = strategy_manager.validate_strategy_params(
            request['strategy_name'], setting
        )
        if not validation_result['valid']:
            return {"success": False, "message": f"策略参数验证失败: {validation_result['message']}"}
        
        # 从数据库加载历史数据
        from vnpy.trader.constant import Exchange, Interval
        exchange_obj = data_converter._get_vnpy_exchange(request['exchange'])
        interval_obj = data_converter._get_vnpy_interval(request['interval'])
        
        start_dt = datetime.fromisoformat(request['start_date'])
        end_dt = datetime.fromisoformat(request['end_date'])
        
        bar_data_list = db_manager.load_bar_data(
            symbol=request['symbol'],
            exchange=exchange_obj,
            interval=interval_obj,
            start=start_dt,
            end=end_dt
        )
        
        if not bar_data_list:
            return {"success": False, "message": "未找到历史数据，请先下载数据"}
        
        # 运行回测
        result = backtest_manager.run_backtest(
            strategy_name=request['strategy_name'],
            bar_data=bar_data_list,
            setting=setting,
            capital=request.get('capital', 100000),
            commission=request.get('commission', 0.0003),
            slippage=request.get('slippage', 0.0001)
        )
        
        return {
            "success": True,
            "message": "�ز����",
            "data": result
        }
        
        if result['success']:
            return {
                "success": True,
                "message": "回测完成",
                "data": result['data']
            }
        else:
            return {"success": False, "message": result['message']}
    
    except Exception as e:
        return {"success": False, "message": f"回测运行失败: {str(e)}"}

@app.get("/api/backtest/results")
async def get_backtest_results(limit: int = 10):
    """获取回测结果列表"""
    try:
        results = backtest_manager.get_backtest_history(limit=limit)
        return {"success": True, "data": results}
    except Exception as e:
        return {"success": False, "message": f"获取回测结果失败: {str(e)}"}

@app.get("/api/backtest/result/{result_id}")
async def get_backtest_result(result_id: str):
    """获取单个回测结果详情"""
    try:
        result = backtest_manager.get_backtest_result(result_id)
        if result:
            return {"success": True, "data": result}
        else:
            return {"success": False, "message": "回测结果不存在"}
    except Exception as e:
        return {"success": False, "message": f"获取回测结果失败: {str(e)}"}

@app.delete("/api/backtest/result/{result_id}")
async def delete_backtest_result(result_id: str):
    """删除回测结果"""
    try:
        success = backtest_manager.delete_backtest_result(result_id)
        if success:
            return {"success": True, "message": "删除成功"}
        else:
            return {"success": False, "message": "回测结果不存在"}
    except Exception as e:
        return {"success": False, "message": f"删除失败: {str(e)}"}

# --- 10. 技术指标API ---
@app.get("/api/indicators/supported")
async def get_supported_indicators():
    """获取支持的技术指标列表"""
    try:
        indicators = technical_indicators.get_supported_indicators()
        return {"success": True, "data": indicators}
    except Exception as e:
        return {"success": False, "message": f"获取指标列表失败: {str(e)}"}

@app.post("/api/indicators/calculate")
async def calculate_indicator(request: dict):
    """计算技术指标"""
    try:
        # 验证请求参数
        required_fields = ['symbol', 'exchange', 'interval', 'indicator']
        for field in required_fields:
            if field not in request:
                return {"success": False, "message": f"缺少必要参数: {field}"}
        
        # 从数据库加载数据
        from vnpy.trader.constant import Exchange, Interval
        exchange_obj = data_converter._get_vnpy_exchange(request['exchange'])
        interval_obj = data_converter._get_vnpy_interval(request['interval'])
        
        start_dt = datetime.fromisoformat(request['start_date']) if request.get('start_date') else None
        end_dt = datetime.fromisoformat(request['end_date']) if request.get('end_date') else None
        
        bar_data_list = db_manager.load_bar_data(
            symbol=request['symbol'],
            exchange=exchange_obj,
            interval=interval_obj,
            start=start_dt,
            end=end_dt
        )
        
        if not bar_data_list:
            return {"success": False, "message": "未找到历史数据"}
        
        # 计算指标
        params = request.get('params', {})
        result = technical_indicators.calculate_from_bars(
            bar_data_list, request['indicator'], **params
        )
        
        if 'error' in result:
            return {"success": False, "message": result['error']}
        else:
            return {"success": True, "data": result}
    
    except Exception as e:
        return {"success": False, "message": f"计算指标失败: {str(e)}"}

@app.post("/api/indicators/batch")
async def calculate_batch_indicators(request: dict):
    """批量计算技术指标"""
    try:
        # 验证请求参数
        required_fields = ['symbol', 'exchange', 'interval', 'indicators']
        for field in required_fields:
            if field not in request:
                return {"success": False, "message": f"缺少必要参数: {field}"}
        
        # 从数据库加载数据
        from vnpy.trader.constant import Exchange, Interval
        exchange_obj = data_converter._get_vnpy_exchange(request['exchange'])
        interval_obj = data_converter._get_vnpy_interval(request['interval'])
        
        start_dt = datetime.fromisoformat(request['start_date']) if request.get('start_date') else None
        end_dt = datetime.fromisoformat(request['end_date']) if request.get('end_date') else None
        
        bar_data_list = db_manager.load_bar_data(
            symbol=request['symbol'],
            exchange=exchange_obj,
            interval=interval_obj,
            start=start_dt,
            end=end_dt
        )
        
        if not bar_data_list:
            return {"success": False, "message": "未找到历史数据"}
        
        # 批量计算指标
        indicators = request['indicators']
        results = technical_indicators.batch_calculate(bar_data_list, indicators)
        
        return {"success": True, "data": results}
    
    except Exception as e:
        return {"success": False, "message": f"批量计算指标失败: {str(e)}"}

# --- 11. WebSocket端点 ---
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

