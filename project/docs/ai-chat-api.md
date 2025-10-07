# AI投资助手API文档

## 概述

AI投资助手模块提供智能化的股票投资咨询服务，通过自然语言处理技术，为用户提供个性化的投资建议、股票分析、市场洞察和风险评估等功能。

## 功能特点

- 🤖 **智能对话**：支持自然语言交互，理解用户投资意图
- 📊 **实时分析**：基于实时市场数据提供分析建议
- 💡 **个性化建议**：根据用户问题生成针对性的投资建议
- 📈 **多维分析**：涵盖技术分析、基本面分析、风险评估
- 🎯 **智能推荐**：提供相关问题建议和投资机会
- 📚 **知识问答**：投资知识普及和教学指导

## API端点列表

### 1. AI聊天对话

**端点：** `POST /api/v1/ai/chat`

**描述：** 与AI投资助手进行对话交流

**请求参数：**
```json
{
  "message": "今天股市表现如何？",
  "conversation_id": "conv_12345",
  "include_context": true
}
```

**参数说明：**
- `message` (required, string): 用户消息内容
- `conversation_id` (optional, string): 对话ID，用于维持上下文
- `include_context` (optional, boolean): 是否包含对话上下文，默认true

**响应示例：**
```json
{
  "success": true,
  "data": {
    "reply": "📊 **今日市场概况**\n\n📈 **上证指数**: 3245.67 (+15.23, +0.47%)\n📈 **深证成指**: 12456.89 (+45.67, +0.37%)\n📉 **创业板指**: 2789.45 (-12.34, -0.44%)\n\n💡 **投资建议**: 请根据市场趋势和个人风险偏好做出投资决策。建议分散投资，控制仓位。",
    "conversation_id": "conv_12345",
    "message_id": "msg_1640995200",
    "stocks_mentioned": ["000001", "399001", "399006"],
    "suggestions": [
      "哪些板块今天表现最好？",
      "推荐一些抗跌股票",
      "现在适合买入吗？"
    ],
    "confidence": 0.9,
    "sources": [
      {
        "type": "实时数据",
        "title": "主要指数实时数据",
        "url": null
      }
    ],
    "timestamp": "2024-01-01T10:00:00Z"
  },
  "message": "AI回复生成成功"
}
```

### 2. 获取建议问题

**端点：** `GET /api/v1/ai/suggestions`

**描述：** 获取AI建议的问题列表

**参数：**
- `context` (optional, string): 上下文关键词

**响应示例：**
```json
{
  "success": true,
  "data": {
    "questions": [
      "今天股市表现如何？",
      "推荐一些科技股",
      "如何控制投资风险？",
      "什么是价值投资？",
      "如何看懂K线图？",
      "新手应该买什么股票？"
    ]
  },
  "message": "获取建议问题成功"
}
```

### 3. 股票智能问答

**端点：** `GET /api/v1/ai/stock-qa/{symbol}`

**描述：** 获取特定股票的智能问答

**参数：**
- `symbol` (path, string): 股票代码

**响应示例：**
```json
{
  "success": true,
  "data": {
    "questions": [
      "000001这只股票怎么样？",
      "分析一下000001的投资价值",
      "000001的技术指标如何？",
      "000001适合长期持有吗？",
      "000001的风险评级是多少？"
    ],
    "basic_info": {
      "symbol": "000001",
      "name": "平安银行",
      "currentPrice": 12.45,
      "change": 0.23,
      "changePercent": 1.88,
      "pe": 6.5,
      "pb": 0.8
    },
    "suggestions": [
      "查看同行业其他股票",
      "了解该股票的财务指标",
      "分析技术走势图",
      "评估投资风险"
    ]
  },
  "message": "获取股票问答成功"
}
```

### 4. 市场洞察

**端点：** `GET /api/v1/ai/market-insights`

**描述：** 获取AI生成的市场洞察和分析

**参数：**
- `timeframe` (optional, string): 时间范围（today/week/month）

**响应示例：**
```json
{
  "success": true,
  "data": {
    "insights": {
      "market_summary": "当前市场整体表现较为活跃，主要指数普遍上涨。",
      "key_trends": [
        "科技股持续受到关注",
        "新能源板块表现活跃",
        "金融股估值优势明显",
        "消费板块分化显著"
      ],
      "sector_highlights": [
        {
          "sector": "科技",
          "performance": 2.3,
          "analysis": "人工智能和芯片概念持续活跃"
        },
        {
          "sector": "新能源",
          "performance": 1.8,
          "analysis": "政策利好推动板块上涨"
        }
      ],
      "risk_factors": [
        "宏观经济不确定性",
        "地缘政治风险",
        "流动性变化风险"
      ],
      "opportunities": [
        "低估值蓝筹股机会",
        "科技创新主题投资",
        "结构性行情机会"
      ]
    },
    "timestamp": "2024-01-01T10:00:00Z"
  },
  "message": "获取市场洞察成功"
}
```

### 5. 批量股票分析

**端点：** `POST /api/v1/ai/analyze-stocks`

**描述：** 批量分析多只股票

**请求参数：**
```json
{
  "symbols": ["000001", "000002", "600036"],
  "question": "哪只股票更有投资价值？"
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "analysis": [
      {
        "symbol": "000001",
        "name": "平安银行",
        "analysis": "基于当前市场环境和投资价值分析，该股票表现良好。",
        "score": 75,
        "recommendation": "hold"
      }
    ],
    "summary": "根据分析，3只股票的平均评分为75.0分。",
    "comparison": "在对比分析中，建议重点关注评分较高的股票，同时注意风险控制。"
  },
  "message": "股票分析完成"
}
```

### 6. 投资组合分析

**端点：** `POST /api/v1/ai/analyze-portfolio`

**描述：** 分析用户投资组合并提供优化建议

**请求参数：**
```json
{
  "holdings": [
    {
      "symbol": "000001",
      "quantity": 1000,
      "average_cost": 12.0
    },
    {
      "symbol": "600036",
      "quantity": 500,
      "average_cost": 35.0
    }
  ]
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "analysis": {
      "total_value": 67500,
      "total_return": 2500,
      "risk_score": 70,
      "diversification_score": 60,
      "sector_allocation": {
        "科技": 40,
        "金融": 30,
        "消费": 20,
        "其他": 10
      },
      "recommendations": [
        "建议进一步分散投资组合",
        "关注高质量蓝筹股",
        "定期调整仓位配比"
      ],
      "rebalancing_suggestions": [
        {
          "action": "buy",
          "symbol": "000001",
          "reason": "增加金融板块配置",
          "priority": "medium"
        }
      ]
    }
  },
  "message": "投资组合分析完成"
}
```

### 7. 风险评估

**端点：** `POST /api/v1/ai/risk-assessment`

**描述：** 评估投资组合的风险水平

**请求参数：**
```json
{
  "portfolio": {
    "holdings": [
      {
        "symbol": "000001",
        "weight": 0.3
      },
      {
        "symbol": "600036",
        "weight": 0.7
      }
    ]
  },
  "timeframe": 30
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "risk_assessment": {
      "overall_risk": "medium",
      "var_95": 0.15,
      "max_drawdown": 0.08,
      "volatility": 0.25,
      "correlation_risks": [
        "同行业股票相关性较高"
      ],
      "concentration_risks": [
        "单一股票持仓过重"
      ],
      "recommendations": [
        "建议分散投资降低风险",
        "增加债券等低风险资产配置"
      ]
    }
  },
  "message": "风险评估完成"
}
```

## 消息意图识别

AI系统能够识别以下用户意图：

1. **问候意图**：你好、您好、嗨等
2. **市场查询**：市场、大盘、指数、行情等
3. **股票分析**：分析、怎么样、如何、评价等
4. **投资建议**：推荐、买什么、投资、选股等
5. **技术分析**：技术指标、MA、RSI等
6. **风险评估**：风险、安全、亏损等

## 实体提取

系统能够从用户消息中提取：

- **股票代码**：6位数字格式
- **板块名称**：科技、金融、医药等
- **数字信息**：价格、百分比等

## 错误处理

所有API在出错时返回统一格式：

```json
{
  "success": false,
  "error": "错误描述",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## 使用示例

### JavaScript/TypeScript
```javascript
// 发送聊天消息
const chatResponse = await fetch('/api/v1/ai/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    message: '今天股市表现如何？',
    conversation_id: 'my_conversation',
    include_context: true
  })
});

// 获取建议问题
const suggestions = await fetch('/api/v1/ai/suggestions?context=股票');

// 股票分析
const analysis = await fetch('/api/v1/ai/analyze-stocks', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    symbols: ['000001', '600036'],
    question: '哪只股票更有投资价值？'
  })
});
```

### Python
```python
import requests

# AI聊天
chat_response = requests.post('/api/v1/ai/chat', json={
    'message': '推荐一些科技股',
    'conversation_id': 'python_client',
    'include_context': True
})

# 市场洞察
insights = requests.get('/api/v1/ai/market-insights', params={
    'timeframe': 'today'
})

# 投资组合分析
portfolio_analysis = requests.post('/api/v1/ai/analyze-portfolio', json={
    'holdings': [
        {'symbol': '000001', 'quantity': 1000, 'average_cost': 12.0}
    ]
})
```

## 注意事项

1. **AI局限性**: 当前AI基于规则和模板生成回复，未集成真实的机器学习模型
2. **数据依赖**: 分析结果依赖实时股票数据的可用性
3. **风险提示**: AI建议仅供参考，投资决策需要用户自主判断
4. **认证要求**: 所有接口支持可选JWT认证
5. **频率限制**: 建议合理控制API调用频率
6. **上下文管理**: conversation_id用于维持对话上下文，提高交互体验

## 扩展功能

### 未来可扩展的功能包括：

1. **真实AI模型集成**: 接入GPT、Claude等大语言模型
2. **情感分析**: 分析用户投资情绪
3. **个性化学习**: 基于用户行为优化建议
4. **多模态交互**: 支持图表、语音等交互方式
5. **实时推送**: WebSocket实时投资提醒
6. **策略回测**: AI辅助投资策略验证