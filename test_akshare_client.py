import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from data_service.akshare_client import AKShareClient

async def test_akshare_client():
    client = AKShareClient()
    
    try:
        print("Testing AKShareClient.get_stock_data...")
        df = await client.get_stock_data(
            symbol="000001",
            period="daily", 
            start_date="2024-01-01",
            end_date="2024-01-31"
        )
        print(f"Success: Got {len(df)} rows")
        if len(df) > 0:
            print(f"Columns: {list(df.columns)}")
            print(f"First row: {df.iloc[0].to_dict()}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_akshare_client())