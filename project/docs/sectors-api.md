# 板块行情API文档

## 概述

板块行情模块提供中国A股市场板块相关数据，包括板块列表、成分股、排行榜、搜索等功能。

## API端点列表

### 1. 获取板块列表

**端点：** `GET /api/v1/sectors`

**描述：** 获取所有板块的基础信息

**参数：**
- `limit` (optional, int): 限制返回数量，默认100，最大200

**响应示例：**
```json
{
  "success": true,
  "data": {
    "sectors": [
      {
        "code": "电子信息",
        "name": "电子信息",
        "currentPrice": 0,
        "change": 2.45,
        "changePercent": 2.45,
        "volume": 0,
        "turnover": 0,
        "stockCount": 156,
        "leadingStocks": []
      }
    ],
    "total": 50,
    "timestamp": "2024-01-01 10:00:00"
  },
  "message": "获取板块列表成功"
}
```

### 2. 获取板块详细信息

**端点：** `GET /api/v1/sectors/{sector_code}`

**描述：** 获取指定板块的详细信息

**参数：**
- `sector_code` (path, string): 板块代码或名称

**响应示例：**
```json
{
  "success": true,
  "data": {
    "sector": {
      "code": "电子信息",
      "name": "电子信息",
      "currentPrice": 0,
      "change": 2.45,
      "changePercent": 2.45,
      "volume": 0,
      "turnover": 0,
      "stockCount": 156,
      "leadingStocks": ["立讯精密", "海康威视", "京东方A"]
    },
    "timestamp": "2024-01-01 10:00:00"
  },
  "message": "获取板块信息成功"
}
```

### 3. 获取板块成分股

**端点：** `GET /api/v1/sectors/{sector_code}/stocks`

**描述：** 获取指定板块的所有成分股信息

**参数：**
- `sector_code` (path, string): 板块代码或名称

**响应示例：**
```json
{
  "success": true,
  "data": {
    "sector_code": "电子信息",
    "stocks": [
      {
        "symbol": "002475",
        "name": "立讯精密",
        "currentPrice": 32.45,
        "change": 1.25,
        "changePercent": 4.00,
        "volume": 125438970,
        "turnover": 4065230000,
        "marketCap": 228560000000,
        "pe": 18.5,
        "pb": 3.2
      }
    ],
    "total": 156,
    "timestamp": "2024-01-01 10:00:00"
  },
  "message": "获取板块成分股成功"
}
```

### 4. 获取热门板块

**端点：** `GET /api/v1/sectors/hot`

**描述：** 获取按涨跌幅排序的热门板块

**参数：**
- `limit` (optional, int): 限制返回数量，默认20，最大100

**响应示例：**
```json
{
  "success": true,
  "data": {
    "sectors": [
      {
        "code": "人工智能",
        "name": "人工智能",
        "currentPrice": 0,
        "change": 5.67,
        "changePercent": 5.67,
        "volume": 0,
        "turnover": 0,
        "stockCount": 89,
        "leadingStocks": ["科大讯飞", "海康威视"]
      }
    ],
    "total": 20,
    "timestamp": "2024-01-01 10:00:00"
  },
  "message": "获取热门板块成功"
}
```

### 5. 搜索板块

**端点：** `GET /api/v1/sectors/search`

**描述：** 根据关键词搜索板块

**参数：**
- `keyword` (required, string): 搜索关键词
- `limit` (optional, int): 限制返回数量，默认10，最大50

**响应示例：**
```json
{
  "success": true,
  "data": {
    "sectors": [
      {
        "code": "电子信息",
        "name": "电子信息",
        "currentPrice": 0,
        "change": 2.45,
        "changePercent": 2.45,
        "volume": 0,
        "turnover": 0,
        "stockCount": 156,
        "leadingStocks": []
      }
    ],
    "total": 3,
    "keyword": "电子",
    "timestamp": "2024-01-01 10:00:00"
  },
  "message": "搜索板块成功"
}
```

### 6. 获取板块排行榜

**端点：** `GET /api/v1/sectors/ranking`

**描述：** 获取按指定指标排序的板块排行榜

**参数：**
- `sort_by` (optional, string): 排序字段，可选值：changePercent, change, volume, turnover, stockCount，默认changePercent
- `order` (optional, string): 排序顺序，可选值：asc, desc，默认desc
- `limit` (optional, int): 限制返回数量，默认50，最大100

**响应示例：**
```json
{
  "success": true,
  "data": {
    "sectors": [
      {
        "code": "人工智能",
        "name": "人工智能",
        "currentPrice": 0,
        "change": 5.67,
        "changePercent": 5.67,
        "volume": 0,
        "turnover": 0,
        "stockCount": 89,
        "leadingStocks": []
      }
    ],
    "total": 50,
    "sort_by": "changePercent",
    "order": "desc",
    "timestamp": "2024-01-01 10:00:00"
  },
  "message": "获取板块排行榜成功"
}
```

### 7. 获取板块分析

**端点：** `GET /api/v1/sectors/{sector_code}/analysis`

**描述：** 获取指定板块的分析数据（基础版本）

**参数：**
- `sector_code` (path, string): 板块代码或名称

**响应示例：**
```json
{
  "success": true,
  "data": {
    "analysis": {
      "sector_code": "电子信息",
      "sector_name": "电子信息",
      "trend_analysis": {
        "short_term": "bullish",
        "medium_term": "neutral",
        "long_term": "neutral"
      },
      "performance": {
        "today": 2.45,
        "week": 0,
        "month": 0,
        "quarter": 0,
        "year": 0
      },
      "risk_level": "medium",
      "recommendation": "当前板块涨跌幅为2.45%，建议根据个人风险承受能力谨慎投资。"
    },
    "timestamp": "2024-01-01 10:00:00"
  },
  "message": "获取板块分析成功"
}
```

## 错误响应

所有API在出错时都会返回统一格式的错误响应：

```json
{
  "success": false,
  "error": "错误描述",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01 10:00:00"
}
```

常见错误码：
- `400`: 请求参数错误
- `404`: 找不到指定板块
- `500`: 服务器内部错误

## 数据字段说明

### 板块信息字段 (SectorInfo)
- `code`: 板块代码
- `name`: 板块名称
- `currentPrice`: 当前价格（板块无具体价格，固定为0）
- `change`: 涨跌额（百分比形式）
- `changePercent`: 涨跌幅百分比
- `volume`: 成交量（需计算成分股总和）
- `turnover`: 成交额（需计算成分股总和）
- `stockCount`: 成分股数量
- `leadingStocks`: 龙头股名称列表

### 成分股字段 (SectorStock)
- `symbol`: 股票代码
- `name`: 股票名称
- `currentPrice`: 当前价格
- `change`: 涨跌额
- `changePercent`: 涨跌幅百分比
- `volume`: 成交量
- `turnover`: 成交额
- `marketCap`: 总市值
- `pe`: 市盈率（可选）
- `pb`: 市净率（可选）

## 使用示例

### JavaScript/TypeScript
```javascript
// 获取热门板块
const response = await fetch('/api/v1/sectors/hot?limit=10');
const data = await response.json();

// 搜索板块
const searchResponse = await fetch('/api/v1/sectors/search?keyword=电子&limit=5');
const searchData = await searchResponse.json();

// 获取板块成分股
const stocksResponse = await fetch('/api/v1/sectors/电子信息/stocks');
const stocksData = await stocksResponse.json();
```

### Python
```python
import requests

# 获取板块排行榜
response = requests.get('/api/v1/sectors/ranking', params={
    'sort_by': 'changePercent',
    'order': 'desc',
    'limit': 20
})
data = response.json()

# 获取板块分析
analysis_response = requests.get('/api/v1/sectors/电子信息/analysis')
analysis_data = analysis_response.json()
```

## 注意事项

1. **数据源依赖**: 板块数据来源于AkShare，受网络环境和数据源限制影响
2. **缓存机制**: 所有接口都有缓存机制，缓存时间为5-10分钟
3. **请求频率**: 建议控制请求频率，避免过于频繁的API调用
4. **认证要求**: 所有接口都支持可选JWT认证，未认证用户也可访问
5. **实时性**: 数据更新频率取决于AkShare数据源的更新频率