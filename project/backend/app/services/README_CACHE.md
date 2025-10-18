# 这是一个示例，展示如何修改现有的服务代码

1. 在 fundamental_analysis.py 中，将下面这段代码：

```python
def get_financial_indicators(self, symbol: str) -> Dict[str, Any]:
    """
    获取股票财务指标
    包括：营业收入、净利润、资产负债、现金流等
    """
    try:
        # 获取财务指标数据
        def get_financial_data():
            return ak.stock_financial_analysis_indicator(symbol=symbol)

        df = self._retry_akshare_call(get_financial_data, max_retries=3, delay=2)

        if df is None or df.empty:
            logger.warning(f"未获取到财务指标数据: {symbol}")
            return {}
```

修改为：

```python
def get_financial_indicators(self, symbol: str) -> Dict[str, Any]:
    """
    获取股票财务指标
    包括：营业收入、净利润、资产负债、现金流等
    """
    try:
        def fetch_data():
            try:
                df = self._retry_akshare_call(
                    lambda: ak.stock_financial_analysis_indicator(symbol=symbol),
                    max_retries=3,
                    delay=2
                )
                return df if df is not None and not df.empty else None
            except Exception as e:
                logger.error(f"获取财务指标失败 {symbol}: {e}")
                return None

        # 使用缓存管理器
        df = cache_manager.get_or_update(
            data_type='financial_indicators',
            identifier=symbol,
            data_fetcher=fetch_data,
            max_age_hours=24  # 24小时更新一次
        )

        if df is None or df.empty:
            logger.warning(f"未获取到财务指标数据: {symbol}")
            return {}
```

2. 修改其他获取数据的方法，例如 get_stock_spot_data：

```python
def get_stock_spot_data(self, symbol: str) -> Optional[Dict]:
    """获取股票实时数据"""
    def fetch_data():
        try:
            df = self._retry_akshare_call(lambda: ak.stock_zh_a_spot_em())
            if df is not None and not df.empty:
                stock_data = df[df['代码'] == symbol]
                if not stock_data.empty:
                    return stock_data
        except Exception as e:
            logger.error(f"获取实时数据失败 {symbol}: {e}")
        return None

    # 实时数据缓存时间较短
    data = cache_manager.get_or_update(
        data_type='stock_spot',
        identifier=symbol,
        data_fetcher=fetch_data,
        max_age_hours=0.1  # 6分钟更新一次
    )

    if data is not None and not data.empty:
        return data.iloc[0].to_dict()
    return None
```

3. 使用缓存的一些建议：

- 对于实时数据（如股票行情），使用较短的缓存时间（5-10分钟）
- 对于财务数据，使用较长的缓存时间（24小时或更长）
- 在缓存获取失败时，尝试返回过期的缓存数据
- 记录详细的日志，便于调试和监控

4. 缓存时间建议：

- 实时行情数据：5-10分钟
- 日线数据：24小时
- 财务报表数据：24小时
- 公司基本信息：7天

5. 错误处理建议：

- 在数据获取失败时返回None而不是空DataFrame
- 在缓存层处理异常，不要让异常传播到业务层
- 记录详细的错误日志
- 实现降级策略（如使用过期数据）