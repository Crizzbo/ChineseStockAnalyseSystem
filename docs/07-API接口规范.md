# API接口规范文档 - 前后端接口契约

## 1. 接口设计原则

### 1.1 RESTful API设计规范
- **资源导向**：URL表示资源，HTTP方法表示操作
- **无状态**：每个请求包含处理所需的全部信息
- **统一接口**：标准化的请求和响应格式
- **分层系统**：支持负载均衡、缓存等中间层

### 1.2 URL命名规范
```
Base URL: https://api.stockanalysis.com/v1

资源命名：
- 使用复数名词：/stocks, /users, /portfolios
- 使用小写字母和连字符：/market-indices
- 避免动词：使用HTTP方法表示动作

示例：
GET /api/v1/stocks              # 获取股票列表
GET /api/v1/stocks/{symbol}     # 获取特定股票
POST /api/v1/analysis           # 创建分析任务
```

### 1.3 HTTP状态码规范
```
成功响应：
200 OK                  # 请求成功
201 Created            # 资源创建成功
204 No Content         # 成功但无返回内容

客户端错误：
400 Bad Request        # 请求参数错误
401 Unauthorized       # 未认证
403 Forbidden         # 权限不足
404 Not Found         # 资源不存在
409 Conflict          # 资源冲突
422 Unprocessable Entity # 请求格式正确但语义错误

服务器错误：
500 Internal Server Error # 服务器内部错误
502 Bad Gateway          # 网关错误
503 Service Unavailable  # 服务不可用
```

## 2. 通用响应格式

### 2.1 成功响应格式
```typescript
interface SuccessResponse<T> {
  success: true;
  data: T;
  message?: string;
  timestamp: string;
  requestId: string;
}

// 示例
{
  "success": true,
  "data": {
    "symbol": "000001",
    "name": "平安银行",
    "price": 12.34
  },
  "message": "数据获取成功",
  "timestamp": "2024-01-15T10:30:00Z",
  "requestId": "req-123456789"
}
```

### 2.2 错误响应格式
```typescript
interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: any;
  };
  timestamp: string;
  requestId: string;
}

// 示例
{
  "success": false,
  "error": {
    "code": "STOCK_NOT_FOUND",
    "message": "股票代码 999999 不存在",
    "details": {
      "symbol": "999999",
      "suggestions": ["000001", "000002"]
    }
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "requestId": "req-123456789"
}
```

### 2.3 分页响应格式
```typescript
interface PaginatedResponse<T> {
  success: true;
  data: T[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
  timestamp: string;
  requestId: string;
}
```

## 3. 认证和授权

### 3.1 JWT认证
```typescript
// 请求头格式
Headers: {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  "Content-Type": "application/json"
}

// JWT Token结构
interface JWTPayload {
  userId: string;
  username: string;
  email: string;
  roles: string[];
  iat: number;  // 签发时间
  exp: number;  // 过期时间
}
```

### 3.2 认证接口
```typescript
// 用户注册
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "user123",
  "email": "user@example.com",
  "password": "securepassword"
}

Response:
{
  "success": true,
  "data": {
    "userId": "usr_123456",
    "username": "user123",
    "email": "user@example.com",
    "accessToken": "eyJhbGciOiJIUzI1NiIs...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIs...",
    "expiresIn": 3600
  }
}

// 用户登录
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}

// Token刷新
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
}
```

## 4. 股票数据接口

### 4.1 基础股票数据
```typescript
// 股票搜索
GET /api/v1/stocks/search?q={query}&limit={limit}&offset={offset}

Response:
{
  "success": true,
  "data": [
    {
      "symbol": "000001",
      "name": "平安银行",
      "market": "SZ",
      "industry": "银行",
      "currentPrice": 12.34,
      "changePercent": 2.45
    }
  ]
}

// 股票基本信息
GET /api/v1/stocks/{symbol}/info

Response:
{
  "success": true,
  "data": {
    "symbol": "000001",
    "name": "平安银行",
    "market": "SZ",
    "industry": "银行",
    "description": "中国平安保险(集团)股份有限公司控股的全国性股份制商业银行",
    "listingDate": "1991-04-03",
    "totalShares": 19405918198,
    "floatShares": 18794262158,
    "marketCap": 239397104884.32,
    "website": "http://bank.pingan.com"
  }
}

// 实时行情
GET /api/v1/stocks/{symbol}/realtime

Response:
{
  "success": true,
  "data": {
    "symbol": "000001",
    "name": "平安银行",
    "currentPrice": 12.34,
    "change": 0.29,
    "changePercent": 2.41,
    "open": 12.05,
    "high": 12.45,
    "low": 11.98,
    "volume": 58293847,
    "turnover": 714581234.56,
    "marketCap": 239397104884.32,
    "peRatio": 4.67,
    "pbRatio": 0.52,
    "updateTime": "2024-01-15T15:00:00+08:00"
  },
  "source": "akshare"
}
```

### 4.2 历史数据接口
```typescript
// 历史价格数据
GET /api/v1/stocks/{symbol}/history?period={period}&adjust={adjust}&start={start}&end={end}

Parameters:
- period: 1d, 5d, 1m, 3m, 6m, 1y, 2y, 5y, max
- adjust: none, qfq(前复权), hfq(后复权)
- start: 开始日期 (YYYY-MM-DD)
- end: 结束日期 (YYYY-MM-DD)

Response:
{
  "success": true,
  "data": [
    {
      "date": "2024-01-15",
      "open": 12.05,
      "high": 12.45,
      "low": 11.98,
      "close": 12.34,
      "volume": 58293847,
      "turnover": 714581234.56,
      "change": 0.29,
      "changePercent": 2.41
    }
  ],
  "params": {
    "period": "1m",
    "adjust": "qfq"
  }
}

// 分钟级数据
GET /api/v1/stocks/{symbol}/history/minute?period={period}&date={date}

Parameters:
- period: 1, 5, 15, 30, 60 (分钟)
- date: 指定日期 (YYYY-MM-DD)

Response:
{
  "success": true,
  "data": [
    {
      "time": "2024-01-15T09:30:00+08:00",
      "open": 12.05,
      "high": 12.08,
      "low": 12.03,
      "close": 12.06,
      "volume": 1234567,
      "turnover": 14876543.21
    }
  ]
}
```

### 4.3 财务数据接口
```typescript
// 财务报表数据
GET /api/v1/stocks/{symbol}/financial/reports?type={type}&period={period}

Parameters:
- type: balance(资产负债表), income(利润表), cashflow(现金流量表)
- period: annual(年报), quarterly(季报)

Response:
{
  "success": true,
  "data": {
    "symbol": "000001",
    "reportType": "balance",
    "period": "annual",
    "reports": [
      {
        "reportDate": "2023-12-31",
        "currency": "CNY",
        "items": {
          "totalAssets": 4567890123456,
          "totalLiabilities": 4123456789012,
          "shareholdersEquity": 444433334444,
          "cashAndEquivalents": 567890123456
        }
      }
    ]
  }
}

// 关键财务指标
GET /api/v1/stocks/{symbol}/financial/indicators?years={years}

Response:
{
  "success": true,
  "data": [
    {
      "year": 2023,
      "quarter": 4,
      "reportDate": "2023-12-31",
      "indicators": {
        "roe": 0.1234,           // 净资产收益率
        "roa": 0.0567,           // 总资产收益率
        "grossMargin": 0.3456,   // 毛利率
        "netMargin": 0.2345,     // 净利率
        "debtToAssetRatio": 0.65, // 资产负债率
        "currentRatio": 1.23,    // 流动比率
        "quickRatio": 0.98,      // 速动比率
        "eps": 1.23,             // 每股收益
        "bvps": 8.45,            // 每股净资产
        "peRatio": 4.67,         // 市盈率
        "pbRatio": 0.52          // 市净率
      }
    }
  ]
}

// 分红数据
GET /api/v1/stocks/{symbol}/dividend?years={years}

Response:
{
  "success": true,
  "data": [
    {
      "year": 2023,
      "announcementDate": "2024-03-15",
      "exDividendDate": "2024-05-20",
      "recordDate": "2024-05-21",
      "paymentDate": "2024-06-15",
      "dividendPerShare": 0.85,
      "dividendYield": 0.0689,
      "payoutRatio": 0.3456
    }
  ]
}
```

### 4.4 技术分析接口
```typescript
// 技术指标
GET /api/v1/stocks/{symbol}/technical/indicators?indicators={indicators}&period={period}

Parameters:
- indicators: ma,ema,macd,rsi,kdj,boll 等 (逗号分隔)
- period: 计算周期数

Response:
{
  "success": true,
  "data": {
    "symbol": "000001",
    "indicators": {
      "ma": {
        "ma5": 12.25,
        "ma10": 12.18,
        "ma20": 12.05,
        "ma60": 11.89
      },
      "macd": {
        "dif": 0.12,
        "dea": 0.08,
        "histogram": 0.04
      },
      "rsi": {
        "rsi6": 62.34,
        "rsi12": 58.76,
        "rsi24": 55.23
      },
      "kdj": {
        "k": 73.45,
        "d": 68.92,
        "j": 82.51
      },
      "boll": {
        "upper": 12.89,
        "middle": 12.34,
        "lower": 11.79
      }
    },
    "updateTime": "2024-01-15T15:00:00+08:00"
  }
}

// 成交量分析
GET /api/v1/stocks/{symbol}/technical/volume?period={period}

Response:
{
  "success": true,
  "data": {
    "symbol": "000001",
    "volumeAnalysis": {
      "avgVolume5": 45678901,
      "avgVolume20": 52341876,
      "volumeRatio": 1.27,
      "turnoverRate": 0.31,
      "volumeTrend": "increasing",
      "volumeProfile": {
        "morningVolume": 23456789,
        "afternoonVolume": 34837058,
        "lastHourVolume": 12847392
      }
    }
  }
}
```

## 5. 市场数据接口

### 5.1 市场概览
```typescript
// 市场指数
GET /api/v1/market/indices

Response:
{
  "success": true,
  "data": [
    {
      "code": "000001",
      "name": "上证指数",
      "currentValue": 3021.45,
      "change": 15.67,
      "changePercent": 0.52,
      "open": 3008.23,
      "high": 3025.89,
      "low": 3005.12,
      "volume": 234567890123,
      "turnover": 345678901234.56
    }
  ]
}

// 市场概况
GET /api/v1/market/summary

Response:
{
  "success": true,
  "data": {
    "tradingDate": "2024-01-15",
    "marketStatus": "open",  // open, closed, pre_open, after_hours
    "totalStocks": 5234,
    "risingStocks": 2876,
    "fallingStocks": 1998,
    "unchangedStocks": 360,
    "risingRatio": 0.5493,
    "totalVolume": 567890123456,
    "totalTurnover": 789012345678.90,
    "avgChangePercent": 0.23
  }
}

// 涨跌幅排行
GET /api/v1/market/ranking?type={type}&limit={limit}

Parameters:
- type: gainers(涨幅), losers(跌幅), volume(成交量), turnover(成交额)
- limit: 返回数量 (默认20)

Response:
{
  "success": true,
  "data": {
    "type": "gainers",
    "stocks": [
      {
        "symbol": "300123",
        "name": "示例股票",
        "currentPrice": 25.67,
        "change": 2.33,
        "changePercent": 9.98,
        "volume": 12345678,
        "turnover": 317234567.89,
        "reason": "业绩超预期"
      }
    ]
  }
}
```

### 5.2 行业分析
```typescript
// 行业列表
GET /api/v1/market/industries

Response:
{
  "success": true,
  "data": [
    {
      "code": "bank",
      "name": "银行",
      "stockCount": 42,
      "avgChangePercent": 1.23,
      "totalMarketCap": 12345678901234.56,
      "topStocks": ["000001", "600036", "601988"]
    }
  ]
}

// 行业详情
GET /api/v1/market/industries/{industryCode}

Response:
{
  "success": true,
  "data": {
    "code": "bank",
    "name": "银行",
    "description": "银行业详细描述...",
    "statistics": {
      "stockCount": 42,
      "avgPeRatio": 4.67,
      "avgPbRatio": 0.52,
      "avgRoe": 0.1234,
      "totalMarketCap": 12345678901234.56
    },
    "stocks": [
      {
        "symbol": "000001",
        "name": "平安银行",
        "currentPrice": 12.34,
        "marketCap": 239397104884.32,
        "peRatio": 4.67
      }
    ]
  }
}
```

## 6. 分析服务接口

### 6.1 AI分析
```typescript
// 综合股票分析
POST /api/v1/analysis/comprehensive/{symbol}
Content-Type: application/json

{
  "analysisType": "comprehensive",  // basic, fundamental, technical, comprehensive
  "timeHorizon": "medium_term",     // short_term, medium_term, long_term
  "riskProfile": "moderate"         // conservative, moderate, aggressive
}

Response:
{
  "success": true,
  "data": {
    "analysisId": "ana_123456789",
    "symbol": "000001",
    "analysisType": "comprehensive",
    "analysisTime": "2024-01-15T10:30:00Z",

    "fundamentalAnalysis": {
      "score": 78,
      "strengths": [
        "净资产收益率较高",
        "负债率控制良好"
      ],
      "weaknesses": [
        "营收增长放缓"
      ],
      "keyMetrics": {
        "roe": 0.1234,
        "roa": 0.0567,
        "debtRatio": 0.45
      }
    },

    "technicalAnalysis": {
      "score": 65,
      "trend": "sideways",
      "support": 11.80,
      "resistance": 12.80,
      "signals": [
        {
          "type": "buy",
          "strength": 0.6,
          "reason": "RSI超卖反弹"
        }
      ]
    },

    "comprehensiveAssessment": {
      "overallScore": 72,
      "recommendation": {
        "action": "hold",           // buy, hold, sell
        "confidence": 0.75,
        "targetPrice": 13.50,
        "timeHorizon": "3-6个月",
        "reasoning": [
          "基本面稳健但估值合理",
          "技术面短期震荡整理",
          "建议等待更好买点"
        ]
      }
    },

    "riskAssessment": {
      "overallRiskLevel": "medium",  // low, medium, high
      "riskScore": 0.45,
      "riskFactors": [
        "行业政策变化风险",
        "利率环境变化影响"
      ]
    }
  }
}

// 获取分析报告
GET /api/v1/analysis/reports/{analysisId}

Response:
{
  "success": true,
  "data": {
    "analysisId": "ana_123456789",
    "status": "completed",  // pending, processing, completed, failed
    "result": { /* 分析结果同上 */ },
    "createdAt": "2024-01-15T10:30:00Z",
    "completedAt": "2024-01-15T10:31:45Z"
  }
}
```

### 6.2 数据质量评估
```typescript
// 数据质量检查
GET /api/v1/data-quality/{symbol}

Response:
{
  "success": true,
  "data": {
    "symbol": "000001",
    "qualityScore": 0.85,
    "dataCompleteness": {
      "realtime": true,
      "historical": true,
      "financial": true,
      "news": true
    },
    "dataFreshness": {
      "realtime": "2024-01-15T15:00:00+08:00",
      "financial": "2023-12-31",
      "lastUpdate": "2024-01-15T15:00:15+08:00"
    },
    "dataConsistency": {
      "isValid": true,
      "warnings": [],
      "errors": []
    },
    "dataSource": "akshare"
  }
}
```

## 7. 用户投资组合接口

### 7.1 持仓管理
```typescript
// 获取持仓列表
GET /api/v1/portfolio/holdings

Response:
{
  "success": true,
  "data": [
    {
      "id": "holding_123",
      "symbol": "000001",
      "name": "平安银行",
      "quantity": 1000,
      "averagePrice": 11.25,
      "currentPrice": 12.34,
      "marketValue": 12340,
      "costBasis": 11250,
      "totalReturn": 1090,
      "returnRate": 0.0969,
      "dayChange": 290,
      "dayChangePercent": 2.41,
      "weight": 0.15,  // 在投资组合中的权重
      "purchaseDate": "2023-10-15",
      "lastUpdate": "2024-01-15T15:00:00+08:00"
    }
  ]
}

// 添加持仓
POST /api/v1/portfolio/holdings
Content-Type: application/json

{
  "symbol": "000001",
  "quantity": 1000,
  "price": 11.25,
  "date": "2024-01-15",
  "fees": 5.0,
  "type": "buy"  // buy, sell
}

Response:
{
  "success": true,
  "data": {
    "id": "holding_124",
    "symbol": "000001",
    "quantity": 1000,
    "averagePrice": 11.25,
    "totalCost": 11255.0
  }
}

// 投资组合表现
GET /api/v1/portfolio/performance?period={period}

Response:
{
  "success": true,
  "data": {
    "period": "1m",
    "totalValue": 125430.50,
    "totalCost": 118750.00,
    "totalReturn": 6680.50,
    "totalReturnRate": 0.0562,
    "dayChange": 1250.30,
    "dayChangePercent": 1.01,
    "
    "assetAllocation": [
      {
        "industry": "银行",
        "value": 45230.50,
        "weight": 0.36,
        "return": 2340.20
      }
    ],
    "performanceHistory": [
      {
        "date": "2024-01-15",
        "totalValue": 125430.50,
        "totalReturn": 6680.50,
        "dayChange": 1250.30
      }
    ]
  }
}
```

### 7.2 风险分析
```typescript
// 投资组合风险分析
GET /api/v1/portfolio/risk-analysis

Response:
{
  "success": true,
  "data": {
    "overallRisk": "medium",
    "riskScore": 0.65,
    "volatility": 0.18,      // 年化波动率
    "maxDrawdown": 0.12,     // 最大回撤
    "sharpeRatio": 1.25,     // 夏普比率
    "beta": 0.95,            // 相对于市场的贝塔值

    "diversification": {
      "industryConcentration": 0.45,  // 行业集中度
      "stockConcentration": 0.23,     // 个股集中度
      "suggestion": "建议增加行业分散度"
    },

    "riskFactors": [
      {
        "factor": "行业集中风险",
        "impact": "medium",
        "description": "银行股占比过高"
      }
    ],

    "suggestions": [
      "考虑增加科技股配置",
      "适当降低单一股票权重"
    ]
  }
}
```

## 8. 实时数据接口

### 8.1 WebSocket连接
```typescript
// WebSocket连接
ws://api.stockanalysis.com/v1/ws

// 连接认证
{
  "type": "auth",
  "token": "eyJhbGciOiJIUzI1NiIs..."
}

// 订阅股票实时数据
{
  "type": "subscribe",
  "channel": "stock.realtime",
  "symbols": ["000001", "600036", "000002"]
}

// 实时数据推送
{
  "type": "data",
  "channel": "stock.realtime",
  "data": {
    "symbol": "000001",
    "price": 12.34,
    "change": 0.29,
    "changePercent": 2.41,
    "volume": 58293847,
    "timestamp": "2024-01-15T15:00:00+08:00"
  }
}

// 取消订阅
{
  "type": "unsubscribe",
  "channel": "stock.realtime",
  "symbols": ["000001"]
}
```

### 8.2 服务器推送事件 (SSE)
```typescript
// SSE连接
GET /api/v1/events/stream
Headers: {
  "Accept": "text/event-stream",
  "Authorization": "Bearer token..."
}

// 事件格式
event: stock.price
data: {"symbol":"000001","price":12.34,"change":0.29}

event: market.status
data: {"status":"open","message":"市场开盘"}

event: portfolio.update
data: {"totalValue":125430.50,"dayChange":1250.30}
```

## 9. 错误处理

### 9.1 错误代码定义
```typescript
enum ErrorCodes {
  // 通用错误 (1000-1999)
  INVALID_REQUEST = 1000,
  UNAUTHORIZED = 1001,
  FORBIDDEN = 1002,
  NOT_FOUND = 1003,
  RATE_LIMITED = 1004,

  // 股票数据错误 (2000-2999)
  STOCK_NOT_FOUND = 2000,
  INVALID_SYMBOL = 2001,
  DATA_UNAVAILABLE = 2002,
  MARKET_CLOSED = 2003,

  // 分析服务错误 (3000-3999)
  ANALYSIS_FAILED = 3000,
  INSUFFICIENT_DATA = 3001,
  ANALYSIS_TIMEOUT = 3002,

  // 投资组合错误 (4000-4999)
  PORTFOLIO_NOT_FOUND = 4000,
  INSUFFICIENT_FUNDS = 4001,
  INVALID_QUANTITY = 4002,

  // 系统错误 (5000-5999)
  INTERNAL_ERROR = 5000,
  DATABASE_ERROR = 5001,
  EXTERNAL_API_ERROR = 5002
}
```

### 9.2 错误处理示例
```typescript
// 客户端错误处理
const handleApiError = (error: ErrorResponse) => {
  switch (error.error.code) {
    case 'STOCK_NOT_FOUND':
      showNotification('股票代码不存在', 'warning');
      break;
    case 'RATE_LIMITED':
      showNotification('请求过于频繁，请稍后再试', 'warning');
      break;
    case 'INTERNAL_ERROR':
      showNotification('系统错误，请稍后再试', 'error');
      break;
    default:
      showNotification(error.error.message, 'error');
  }
};
```

## 10. API版本管理

### 10.1 版本控制策略
```
版本格式: v{major}.{minor}
- major: 重大变更，不兼容旧版本
- minor: 功能增加，向下兼容

当前版本: v1.0
URL格式: /api/v1/...

版本废弃政策:
- 新版本发布后，旧版本维护6个月
- 提前3个月通知版本废弃
- 重要修复会backport到旧版本
```

### 10.2 API变更日志
```
v1.1 (2024-02-15):
+ 新增实时数据WebSocket接口
+ 新增投资组合风险分析
+ 优化股票搜索性能

v1.0 (2024-01-15):
+ 初始版本发布
+ 基础股票数据接口
+ 用户认证授权
+ AI分析服务
```

---

*本API接口规范确保前后端开发团队的协作效率，为系统集成提供标准化的接口契约。*