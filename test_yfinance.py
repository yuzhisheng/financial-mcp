import yfinance as yf
import time

try:
    # 测试多个股票代码以排除单个代码问题
    test_tickers = [
        "01378.HK",  # 腾讯控股(港股)
        "AAPL",      # 苹果公司(美股)
        "MSFT"       # 微软公司(美股)
    ]
    
    for ticker_symbol in test_tickers:
        print(f"\n=== 测试股票代码: {ticker_symbol} ===")
        ticker = yf.Ticker(ticker_symbol)
        
        # 获取基本信息
        info = ticker.info
        print(f"公司名称: {info.get('longName', '未找到')}")
        print(f"当前价格: {info.get('currentPrice', '未找到')}")
        
        # 获取历史数据
        hist = ticker.history(period="1d")
        print(f"历史数据行数: {len(hist)}")
        
        # 验证数据是否有效
        if info.get('longName') and len(hist) > 0:
            print(f"✅ {ticker_symbol} 数据获取成功")
        else:
            print(f"❌ {ticker_symbol} 数据获取失败")
    
    # 综合判断
    if any(info.get('longName') for ticker_symbol in test_tickers for info in [yf.Ticker(ticker_symbol).info]):
        print("\n测试结果: 网络与yfinance连接正常，但部分股票代码可能存在数据获取问题")
    else:
        print("\n测试结果: 网络连接正常，但所有测试股票代码均无法获取数据")

except Exception as e:
    print(f"测试失败: {str(e)}")
    if 'Failed to get data' in str(e) or 'ConnectionError' in str(e):
        print("可能的原因: 网络连接问题、防火墙阻止或yfinance API变更")