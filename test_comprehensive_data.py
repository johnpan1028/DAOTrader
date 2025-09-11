import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from data_service.akshare_client import AKShareClient
from data_service.data_converter import DataConverter
from data_service.vnpy_database import VnpyDatabaseManager

async def test_comprehensive_data():
    """全面测试不同类型数据的接入"""
    client = AKShareClient()
    converter = DataConverter()
    db_manager = VnpyDatabaseManager()
    
    test_cases = [
        {
            "name": "股票数据",
            "symbol": "000001",
            "exchange": "sz",
            "data_type": "stock"
        },
        {
            "name": "指数数据", 
            "symbol": "000001",
            "exchange": "sz",
            "data_type": "index"
        }
    ]
    
    print("=== 全面数据接入测试 ===")
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试{case['name']}...")
        
        try:
            # 获取数据
            if case['data_type'] == 'stock':
                df = await client.get_stock_data(
                    symbol=case['symbol'],
                    period="daily",
                    start_date="2024-01-01",
                    end_date="2024-01-03"
                )
            elif case['data_type'] == 'index':
                df = await client.get_index_data(
                    symbol=case['symbol'],
                    start_date="2024-01-01",
                    end_date="2024-01-03"
                )
            
            if len(df) == 0:
                print(f"   ❌ 未获取到{case['name']}")
                continue
                
            print(f"   ✓ 获取到 {len(df)} 条{case['name']}")
            
            # 转换格式
            bars = converter.akshare_to_vnpy_bars(
                df=df,
                symbol=case['symbol'],
                exchange=case['exchange'],
                interval="daily"
            )
            
            if len(bars) == 0:
                print(f"   ❌ {case['name']}转换失败")
                continue
                
            print(f"   ✓ 转换为 {len(bars)} 个VNPY对象")
            
            # 保存到数据库
            success = db_manager.save_bar_data(bars)
            
            if not success:
                print(f"   ❌ {case['name']}保存失败")
                continue
                
            print(f"   ✓ {case['name']}保存成功")
            
            # 验证数据
            from vnpy.trader.constant import Exchange, Interval
            saved_bars = db_manager.load_bar_data(
                symbol=case['symbol'],
                exchange=Exchange(case['exchange'].upper()),
                interval=Interval.DAILY,
                start=bars[0].datetime,
                end=bars[-1].datetime
            )
            
            if len(saved_bars) > 0:
                print(f"   ✓ 验证成功，读取到 {len(saved_bars)} 条数据")
                bar = saved_bars[0]
                print(f"   首条数据: {bar.symbol} {bar.datetime} O:{bar.open_price} C:{bar.close_price}")
            else:
                print(f"   ❌ 验证失败，未读取到数据")
                
        except Exception as e:
            print(f"   ❌ {case['name']}测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_comprehensive_data())