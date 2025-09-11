import akshare as ak

print("Testing different stock symbols...")

# Test different symbols
symbols = ['000001', '600734', '000002', '600000']
for symbol in symbols:
    try:
        print(f"\nTesting symbol: {symbol}")
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date="20240101",
            end_date="20240131",
            adjust="qfq"
        )
        print(f"Success: Got {len(df)} rows")
        if len(df) > 0:
            print(f"First date: {df.iloc[0]['日期']}")
    except Exception as e:
        print(f"Error for {symbol}: {e}")
        print(f"Error type: {type(e).__name__}")