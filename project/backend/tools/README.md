# AKShare股票分析工具

基于AKShare库的完整股票数据获取和分析工具包，为股票投资分析提供全面的数据支持和智能分析功能。

## 功能特性

### 🚀 核心功能
- **实时行情数据**: 获取A股实时价格、成交量、涨跌幅等数据
- **历史数据分析**: 支持日线、周线、月线及分钟级历史数据
- **基本面分析**: 财务报表、财务指标、公司基本信息
- **技术分析**: RSI、MACD、布林带等技术指标计算
- **市场情绪分析**: 资金流向、换手率、成交量分析
- **综合评估**: 基于多维度数据的股票综合评分和投资建议

### 🛡️ 可靠性保障
- **智能重试机制**: API调用失败自动重试，指数退避算法
- **数据验证**: 完整的数据质量检验和异常检测
- **缓存优化**: Redis + 文件双重缓存，提升数据访问效率
- **错误处理**: 完善的异常捕获和日志记录

### 📊 分析能力
- **多维度评分**: 基本面、技术面、市场情绪综合评分
- **风险评估**: 量化风险分析和风险等级判断
- **投资建议**: 基于分析结果生成买入/卖出/持有建议
- **趋势识别**: 价格趋势、成交量趋势自动识别

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本使用

```python
from stock_analysis_system import StockAnalysisSystem

# 创建分析系统
system = StockAnalysisSystem(enable_cache=True)

# 分析单只股票
result = system.analyze_stock("000001", analysis_type="comprehensive")

# 查看分析结果
print(f"综合评分: {result['comprehensive_assessment']['overall_score']}")
print(f"投资建议: {result['investment_recommendation']['action']}")
```

### 服务组件使用

```python
# 使用具体服务
from realtime_data_service import RealTimeDataService
from historical_data_service import HistoricalDataService

# 实时数据
realtime_service = RealTimeDataService()
current_data = realtime_service.get_stock_realtime("000001")

# 历史数据
historical_service = HistoricalDataService()
hist_data = historical_service.get_recent_data("000001", days=30)
```

## 系统架构

```
stock_analysis_system.py          # 主分析系统
├── realtime_data_service.py      # 实时数据服务
├── historical_data_service.py    # 历史数据服务
├── fundamental_data_service.py   # 基本面数据服务
├── market_analysis_service.py    # 市场分析服务
├── data_cache_manager.py         # 数据缓存管理
└── utils/                        # 工具模块
    ├── retry_decorator.py        # 重试装饰器
    └── data_validator.py         # 数据验证器
```

## 详细功能

### 1. 实时数据服务 (RealTimeDataService)

- `get_a_share_spot()`: 获取A股实时行情
- `get_stock_realtime(symbol)`: 获取单只股票实时数据
- `get_market_indices()`: 获取主要指数
- `get_market_summary()`: 获取市场概况统计

### 2. 历史数据服务 (HistoricalDataService)

- `get_historical_prices()`: 获取历史价格数据
- `get_minute_data()`: 获取分钟级数据
- `get_weekly_data()`: 获取周线数据
- `get_monthly_data()`: 获取月线数据
- `get_price_statistics()`: 计算价格统计指标

### 3. 基本面数据服务 (FundamentalDataService)

- `get_financial_summary()`: 获取财务摘要
- `get_balance_sheet()`: 获取资产负债表
- `get_income_statement()`: 获取利润表
- `get_cash_flow()`: 获取现金流量表
- `calculate_financial_ratios()`: 计算财务比率

### 4. 市场分析服务 (MarketAnalysisService)

- `get_technical_indicators()`: 计算技术指标
- `get_volume_analysis()`: 成交量分析
- `get_turnover_rate_analysis()`: 换手率分析
- `get_market_sentiment()`: 市场情绪分析

### 5. 缓存管理 (DataCacheManager)

- Redis缓存支持
- 文件缓存备选方案
- 自动过期清理
- 缓存统计和监控

## 配置说明

### 缓存配置

```python
cache_config = {
    'redis_host': 'localhost',
    'redis_port': 6379,
    'redis_db': 0,
    'enable_file_cache': True,
    'file_cache_dir': './cache'
}

system = StockAnalysisSystem(cache_config=cache_config)
```

### 缓存过期时间

- 实时数据: 30秒
- 日线数据: 1小时
- 基本面数据: 1天
- 技术指标: 30分钟

## 数据验证

系统提供完整的数据质量验证功能：

```python
from utils.data_validator import DataValidator

validator = DataValidator()
validation_result = validator.validate_stock_data(data, 'historical')

if validation_result['is_valid']:
    print("数据验证通过")
else:
    print("数据问题:", validation_result['errors'])
```

## 错误处理和重试

内置智能重试机制：

```python
from utils.retry_decorator import retry_on_failure

@retry_on_failure(max_retries=3, delay=1, backoff_factor=2.0)
def your_api_call():
    # 你的API调用代码
    pass
```

## 性能优化

### 批量数据获取

```python
# 批量获取多只股票数据
symbols = ["000001", "000002", "600000"]
results = historical_service.get_multiple_stocks_data(
    symbols, "20240101", "20241201"
)
```

### 数据压缩存储

系统自动使用Parquet格式压缩存储历史数据，大幅节省存储空间。

## API监控

系统内置API调用监控：

```python
from utils.retry_decorator import api_monitor

# 获取API调用统计
stats = api_monitor.get_statistics()
print(f"成功率: {stats['success_rate']:.2%}")
print(f"平均重试次数: {stats['avg_retry_count']:.2f}")
```

## 系统统计

```python
# 获取系统运行统计
stats = system.get_system_stats()
print("API监控:", stats['api_monitor'])
print("缓存统计:", stats['cache_stats'])
```

## 注意事项

### 1. API访问限制
- 建议设置合理的请求频率限制
- 避免短时间内大量API调用
- 充分利用缓存机制减少重复请求

### 2. 数据准确性
- 数据来源于AKShare，请关注数据源的准确性
- 建议在实际投资前验证数据的可靠性
- 系统提供的投资建议仅供参考

### 3. 系统资源
- Redis缓存需要额外的内存资源
- 文件缓存会占用磁盘空间
- 定期清理过期缓存文件

## 故障排除

### 常见问题

1. **Redis连接失败**
   - 检查Redis服务是否运行
   - 验证连接参数是否正确
   - 系统会自动降级到文件缓存

2. **AKShare API调用失败**
   - 检查网络连接
   - 验证股票代码格式
   - 查看重试机制是否生效

3. **数据验证失败**
   - 检查数据完整性
   - 查看验证报告中的具体错误
   - 根据建议进行数据修复

## 示例代码

完整的使用示例请参考 `example_usage.py` 文件。

## 版本历史

- v1.0.0: 初始版本，包含基础功能
  - 实时数据获取
  - 历史数据分析
  - 基本面分析
  - 技术分析
  - 缓存机制
  - 数据验证

## 许可证

MIT License

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 联系方式

如有问题或建议，请通过GitHub Issue联系我们。