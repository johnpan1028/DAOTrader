import sys
sys.path.append('backend')
from data_service.akshare_client import AKShareClient
import asyncio
import traceback

async def test_futures():
    client = AKShareClient()
    try:
        print("开始测试期货数据获取...")
        data = await client.get_futures_data('RB2509', '2024-01-01', '2024-12-31')
        print(f'成功获取数据: {len(data) if data is not None else 0} 条')
        if data is not None and len(data) > 0:
            print(f'数据列名: {data.columns.tolist()}')
            print(f'数据样本:\n{data.head()}')
    except Exception as e:
        print(f'错误: {str(e)}')
        print(f'详细错误: {traceback.format_exc()}')

if __name__ == '__main__':
    asyncio.run(test_futures())