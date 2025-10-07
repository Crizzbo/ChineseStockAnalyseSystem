"""
模拟股票数据 - 用于演示和测试
"""
from datetime import datetime, timedelta
import random

def get_mock_market_indices():
    """获取模拟市场指数数据"""
    return [
        {
            'symbol': 'sh000001',
            'name': '上证指数',
            'currentPrice': 3245.67,
            'change': 12.34,
            'changePercent': 0.38,
            'volume': 125600000,
            'turnover': 234500000000
        },
        {
            'symbol': 'sz399001',
            'name': '深证成指',
            'currentPrice': 12456.78,
            'change': -28.56,
            'changePercent': -0.23,
            'volume': 89750000,
            'turnover': 156700000000
        },
        {
            'symbol': 'sz399006',
            'name': '创业板指',
            'currentPrice': 2789.12,
            'change': 56.78,
            'changePercent': 2.08,
            'volume': 67890000,
            'turnover': 98760000000
        }
    ]

def get_mock_hot_stocks(limit=20):
    """获取模拟热门股票数据"""
    stocks = [
        {
            'symbol': '000001',
            'name': '平安银行',
            'currentPrice': 12.45,
            'change': 0.23,
            'changePercent': 1.88,
            'volume': 156780000,
            'turnover': 1950000000,
            'high': 12.68,
            'low': 12.12,
            'open': 12.22,
            'preClose': 12.22
        },
        {
            'symbol': '600519',
            'name': '贵州茅台',
            'currentPrice': 1650.00,
            'change': -28.50,
            'changePercent': -1.70,
            'volume': 1250000,
            'turnover': 2062500000,
            'high': 1678.50,
            'low': 1632.00,
            'open': 1672.00,
            'preClose': 1678.50
        },
        {
            'symbol': '000858',
            'name': '五粮液',
            'currentPrice': 168.50,
            'change': 2.80,
            'changePercent': 1.69,
            'volume': 8960000,
            'turnover': 1507840000,
            'high': 169.80,
            'low': 165.20,
            'open': 166.00,
            'preClose': 165.70
        },
        {
            'symbol': '600036',
            'name': '招商银行',
            'currentPrice': 42.18,
            'change': 1.25,
            'changePercent': 3.05,
            'volume': 45230000,
            'turnover': 1907053400,
            'high': 42.56,
            'low': 40.89,
            'open': 41.12,
            'preClose': 40.93
        },
        {
            'symbol': '000002',
            'name': '万科A',
            'currentPrice': 18.56,
            'change': -0.45,
            'changePercent': -2.37,
            'volume': 89760000,
            'turnover': 1665849600,
            'high': 19.12,
            'low': 18.34,
            'open': 18.89,
            'preClose': 19.01
        }
    ]

    # 如果需要更多股票，随机生成
    while len(stocks) < limit:
        base_stock = random.choice(stocks[:5])
        new_stock = base_stock.copy()
        new_stock['symbol'] = f"{random.randint(300001, 300999)}"
        new_stock['name'] = f"模拟股票{len(stocks)+1}"
        new_stock['currentPrice'] = round(random.uniform(5, 200), 2)
        change = round(random.uniform(-5, 5), 2)
        new_stock['change'] = change
        new_stock['changePercent'] = round((change / new_stock['currentPrice']) * 100, 2)
        new_stock['volume'] = random.randint(1000000, 100000000)
        stocks.append(new_stock)

    return stocks[:limit]

def get_mock_stock_info(symbol):
    """获取模拟单个股票信息"""
    # 从热门股票中查找
    hot_stocks = get_mock_hot_stocks()
    for stock in hot_stocks:
        if stock['symbol'] == symbol:
            return stock

    # 如果没找到，返回随机数据
    return {
        'symbol': symbol,
        'name': f'股票{symbol}',
        'currentPrice': round(random.uniform(5, 200), 2),
        'change': round(random.uniform(-5, 5), 2),
        'changePercent': round(random.uniform(-10, 10), 2),
        'volume': random.randint(1000000, 100000000),
        'turnover': random.randint(100000000, 5000000000),
        'high': round(random.uniform(5, 200), 2),
        'low': round(random.uniform(5, 200), 2),
        'open': round(random.uniform(5, 200), 2),
        'preClose': round(random.uniform(5, 200), 2),
        'marketCap': random.randint(1000000000, 1000000000000),
        'pe': round(random.uniform(5, 50), 1),
        'pb': round(random.uniform(0.5, 10), 2)
    }

def get_mock_search_results(keyword, limit=10):
    """获取模拟搜索结果"""
    all_stocks = get_mock_hot_stocks(50)  # 获取更多股票用于搜索

    # 模拟搜索匹配
    results = []
    keyword_lower = keyword.lower()

    for stock in all_stocks:
        if (keyword_lower in stock['symbol'].lower() or
            keyword_lower in stock['name'].lower()):
            results.append(stock)
            if len(results) >= limit:
                break

    return results

def get_mock_price_history(symbol, period="daily", limit=250):
    """获取模拟历史价格数据"""
    end_date = datetime.now()
    history_data = []

    base_price = 100.0

    for i in range(limit):
        date = end_date - timedelta(days=limit-i-1)

        # 模拟价格波动
        change = random.uniform(-0.05, 0.05)  # ±5%波动
        base_price *= (1 + change)

        open_price = base_price
        high_price = open_price * random.uniform(1.0, 1.03)
        low_price = open_price * random.uniform(0.97, 1.0)
        close_price = random.uniform(low_price, high_price)

        base_price = close_price  # 下一天的基础价格

        history_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': random.randint(1000000, 50000000),
            'turnover': random.randint(100000000, 2000000000)
        })

    return history_data

def get_mock_technical_indicators(symbol, period="daily"):
    """获取模拟技术指标"""
    return {
        'ma5': round(random.uniform(50, 150), 2),
        'ma10': round(random.uniform(48, 152), 2),
        'ma20': round(random.uniform(45, 155), 2),
        'ma60': round(random.uniform(40, 160), 2),
        'rsi': round(random.uniform(20, 80), 2),
        'volume_ratio': round(random.uniform(0.5, 3.0), 2)
    }